import unittest
import random
import ecs

P, V, H, D = 1, 2, 4, 8

class EcsTests(unittest.TestCase):
    def api(self, name):
        self.assertTrue(hasattr(ecs, name), "missing mechanism: " + name)
        return getattr(ecs, name)

    def test_cache_coverage_distinguishes_stride_and_columns(self):
        coverage = self.api("cache_coverage")
        self.assertEqual(coverage("aos", 64), (64, 1536, 4096))
        self.assertEqual(coverage("soa", 64), (24, 1536, 1536))
        self.assertEqual(coverage("soa", 1), (2, 24, 128))
        self.assertEqual(coverage("aos", 0), (0, 0, 0))

    def test_layout_fits_maximal_capacity_with_padding(self):
        layout = self.api("Layout")(P | V)
        self.assertEqual(layout.capacity, 122)
        self.assertEqual(layout.offsets, {0: 64, P: 1088, V: 2560})
        self.assertEqual(layout.used_bytes, 4024)
        self.assertEqual(self.api("Layout")(P | V | H).capacity, 112)
        self.assertEqual(self.api("Layout")(P | V | H).used_bytes, 4096)
        with self.assertRaises(ValueError): self.api("Layout")(P, block_bytes=64)

    def test_actual_addresses_and_float32_round_trip(self):
        world = self.api("World")()
        world.spawn(4, {P: (1, 2, 3), V: (4, 5, 6)})
        world.spawn(7, {P: (7, 8, 9), V: (1, 2, 3)})
        chunk, row = world.locations[4]
        self.assertEqual(chunk.base_address % 64, 0)
        self.assertEqual(chunk.address(P, 1)-chunk.address(P, 0), 12)
        self.assertEqual(chunk.address(P, 0)-chunk.base_address, 1088)
        self.assertEqual(world.values(7)[P], (7.0, 8.0, 9.0))

    def test_query_matches_superset_and_rejects_missing_or_tagged(self):
        world = self.api("World")()
        world.spawn(1, {P: (0,0,0)})
        world.spawn(2, {P: (0,0,0), V: (1,0,0)})
        world.spawn(3, {P: (0,0,0), V: (1,0,0), H: 10})
        world.spawn(4, {P: (0,0,0), V: (1,0,0), D: None})
        self.assertEqual(sorted(world.query_ids(P|V, D)), [2,3])
        self.assertEqual(sorted(world.query_ids(P|V)), [2,3,4])

    def test_query_cache_sees_new_archetype_and_new_chunk(self):
        world = self.api("World")()
        self.assertEqual(world.query_ids(P|V), [])
        for eid in range(1, 125): world.spawn(eid, {P:(eid,0,0),V:(1,0,0)})
        self.assertEqual(len(world.query_chunks(P|V)), 2)
        self.assertEqual(len(world.query_ids(P|V)), 124)
        world.spawn(200, {P:(0,0,0),V:(0,0,0),H:3})
        self.assertIn(200, world.query_ids(P|V))

    def test_move_first_row_repairs_swapped_entity_and_copies_all_columns(self):
        world = self.api("World")()
        for eid in (4,7,9): world.spawn(eid, {P:(eid,1,2),V:(3,eid,5)})
        source, _ = world.locations[4]
        world.change(4, add={H:80})
        self.assertEqual((source.count, source.entity(0), source.entity(1)), (2,9,7))
        self.assertEqual(world.locations[9], (source,0))
        self.assertEqual(world.values(4), {P:(4.0,1.0,2.0),V:(3.0,4.0,5.0),H:80})
        self.assertEqual(world.values(9)[V], (3.0,9.0,5.0))
        world.change(9, add={H:90})
        self.assertEqual(world.values(9)[H], 90)
        self.assertEqual(world.values(7)[P], (7.0,1.0,2.0))
        world.check_invariants()

    def test_remove_component_and_last_row_path(self):
        world = self.api("World")()
        world.spawn(4, {P:(1,2,3),V:(4,5,6),H:8})
        source, _ = world.locations[4]
        world.change(4, remove=H)
        self.assertEqual(source.count, 0)
        self.assertEqual(world.values(4), {P:(1.0,2.0,3.0),V:(4.0,5.0,6.0)})
        world.change(4, add={D:None})
        self.assertEqual(world.query_ids(P|V,D), [])
        world.check_invariants()

    def test_invalid_input_does_not_remove_source(self):
        world = self.api("World")()
        world.spawn(4, {P:(1,2,3), V:(4,5,6)})
        old_location = world.locations[4]
        with self.assertRaises(ValueError): world.change(4, add={H:2**40})
        with self.assertRaises(ValueError): world.change(4, add={P:(0,0,0)})
        with self.assertRaises(ValueError): world.spawn(4, {P:(0,0,0)})
        self.assertEqual(world.locations[4], old_location)
        self.assertEqual(world.values(4)[V], (4.0,5.0,6.0))
        world.check_invariants()

    def test_iteration_rejects_structure_and_allows_later_flush(self):
        world = self.api("World")()
        world.spawn(4, {P:(0,0,0),V:(1,0,0)})
        with world.iteration():
            with self.assertRaises(RuntimeError): world.change(4,add={H:9})
            with self.assertRaises(RuntimeError): world.spawn(7,{P:(0,0,0)})
        world.change(4,add={H:9})
        self.assertEqual(world.values(4)[H],9)

    def test_integrate_updates_only_matching_active_entities(self):
        world = self.api("World")()
        world.spawn(4,{P:(1,2,3),V:(2,-4,6),H:80})
        world.spawn(7,{P:(9,9,9)})
        world.spawn(9,{P:(8,8,8),V:(5,5,5),D:None})
        world.integrate(0.5)
        self.assertEqual(world.values(4),{P:(2.0,0.0,6.0),V:(2.0,-4.0,6.0),H:80})
        self.assertEqual(world.values(7)[P],(9.0,9.0,9.0))
        self.assertEqual(world.values(9)[P],(8.0,8.0,8.0))
        with self.assertRaises(ValueError): world.integrate(float("nan"))

    def test_repeated_migrations_match_entity_keyed_oracle(self):
        world = self.api("World")()
        expected={}
        for eid in range(1,161):
            expected[eid]={P:(float(eid),0.0,0.0),V:(0.0,float(eid),0.0)}
            world.spawn(eid,expected[eid])
        rng=random.Random(31)
        for _ in range(300):
            eid=rng.randrange(1,161)
            if H in expected[eid]:
                world.change(eid,remove=H);del expected[eid][H]
            else:
                world.change(eid,add={H:eid*2});expected[eid][H]=eid*2
            world.check_invariants()
        self.assertEqual({eid:world.values(eid) for eid in expected},expected)

if __name__ == "__main__": unittest.main(verbosity=2)
