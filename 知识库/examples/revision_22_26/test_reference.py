"""CPU invariants for articles 22–26; no engine or GPU coverage."""
import unittest
from reference import ready_order, move_row, clipped, batch_keys, glyph_quad, mix_mono, occluded, select_cut


class ReferenceTests(unittest.TestCase):
    def test_diamond_dependency(self):
        order = ready_order({'pose': [], 'bounds': ['pose'], 'skin': ['pose'], 'draw': ['bounds', 'skin']})
        self.assertEqual(order, ['pose', 'bounds', 'skin', 'draw'])

    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):
            ready_order({'a': ['b'], 'b': ['a']})

    def test_unknown_dependency_rejected(self):
        with self.assertRaises(ValueError):
            ready_order({'a': ['missing']})

    def test_ecs_swap_updates_moved_entity(self):
        rows = [{'id': 4, 'x': 1}, {'id': 7, 'x': 2}, {'id': 9, 'x': 3}]
        self.assertEqual(move_row(rows, 0, {'tag': 1}),
                         ({'id': 4, 'x': 1, 'tag': 1}, {9: 0, 7: 1}))
        self.assertEqual([r['id'] for r in rows], [9, 7])

    def test_ecs_remove_last(self):
        rows = [{'id': 4}]
        self.assertEqual(move_row(rows, 0, {}), ({'id': 4}, {}))

    def test_nested_clipping(self):
        self.assertEqual(clipped((0, 0, 100, 80), (30, -10, 150, 20)), (30, 0, 100, 20))

    def test_empty_clip_skipped(self):
        self.assertIsNone(clipped((0, 0, 10, 10), (10, 0, 20, 10)))

    def test_batches_preserve_painter_order(self):
        self.assertEqual(batch_keys(['A', 'A', 'B', 'A']), [('A', 2), ('B', 1), ('A', 1)])

    def test_empty_draw_list(self):
        self.assertEqual(batch_keys([]), [])

    def test_glyph_offset_and_bearing(self):
        self.assertEqual(glyph_quad((10, 40), (2, 3), (1, 8), (6, 9)), (13, 29, 19, 38))

    def test_zero_advance_mark_has_separate_position(self):
        self.assertEqual(glyph_quad((20, 40), (-5, 4), (0, 3), (2, 2)), (15, 33, 17, 35))

    def test_audio_sum_remains_float_and_ramps(self):
        self.assertEqual(mix_mono([1, 1, 1], [1, 1, 1], 0, 1), [1, 1.5, 2])

    def test_audio_single_sample_target(self):
        self.assertEqual(mix_mono([0], [1], 0, .5), [.5])

    def test_audio_empty(self):
        self.assertEqual(mix_mono([], [], 0, 1), [])

    def test_forward_hiz_all_samples_covered(self):
        self.assertTrue(occluded(.9, [.2, .7], False))
        self.assertFalse(occluded(.6, [.2, .7], False))

    def test_reverse_hiz_all_samples_covered(self):
        self.assertTrue(occluded(.1, [.8, .3], True))
        self.assertFalse(occluded(.4, [.8, .3], True))

    def test_hiz_background_prevents_rejection(self):
        self.assertFalse(occluded(.9, [.2, 1.0], False))
        self.assertFalse(occluded(.1, [.8, 0.0], True))

    def test_hiz_equal_is_visible(self):
        self.assertFalse(occluded(.3, [.3], False))

    def test_cut_children_cover_parent(self):
        nodes = {'p': (9, ['a', 'b']), 'a': (0, []), 'b': (0, [])}
        self.assertEqual(select_cut(nodes, 'p', {'p','a','b'}, 1), (['a','b'], []))

    def test_cut_missing_sibling_keeps_parent(self):
        nodes = {'p': (9, ['a', 'b']), 'a': (0, []), 'b': (0, [])}
        self.assertEqual(select_cut(nodes, 'p', {'p','a'}, 1), (['p'], ['b']))

    def test_cut_threshold_equality(self):
        self.assertEqual(select_cut({'p': (1, [])}, 'p', {'p'}, 1), (['p'], []))


if __name__ == '__main__':
    unittest.main(verbosity=2)
