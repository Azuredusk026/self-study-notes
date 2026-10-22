"""独立复核补充的边界回归；使用小位宽模拟无符号范围。"""
import unittest
from review_reference import arena_allocate, accept_snapshot, uct_select, goap_plan

class Arena(unittest.TestCase):
    def test_alignment_and_exact_fit(self):
        self.assertEqual(arena_allocate(13,20,16,36,255), (16,36))
    def test_alignment_crosses_capacity(self):
        with self.assertRaises(MemoryError):
            arena_allocate(13,0,16,15,255)
    def test_alignment_addition_overflows(self):
        with self.assertRaises(OverflowError):
            arena_allocate(250,1,16,255,255)
    def test_size_cannot_wrap(self):
        with self.assertRaises(MemoryError):
            arena_allocate(240,32,16,255,255)
    def test_invalid_alignment(self):
        for a in (0,3,-1):
            with self.assertRaises(ValueError):
                arena_allocate(0,1,a,255,255)

class SnapshotVersion(unittest.TestCase):
    def test_same_ack_newer_state_is_accepted(self):
        self.assertTrue(accept_snapshot(100,7,101,7))
    def test_stale_state_is_rejected(self):
        self.assertFalse(accept_snapshot(100,7,99,7))
        self.assertFalse(accept_snapshot(100,7,100,7))
    def test_wrapped_ack_is_accepted(self):
        self.assertTrue(accept_snapshot(100,65535,101,0))
    def test_reversed_ack_is_rejected(self):
        self.assertFalse(accept_snapshot(100,7,101,6))

class Search(unittest.TestCase):
    def test_uct_root_maximizes(self):
        self.assertEqual(uct_select([(4,3.0),(4,-2.0)],8,1.0,1),0)
    def test_uct_opponent_minimizes_root_value(self):
        self.assertEqual(uct_select([(4,3.0),(4,-2.0)],8,1.0,-1),1)
    def test_uct_explores_unvisited(self):
        self.assertEqual(uct_select([(4,3.0),(0,0.0)],4,1.0,-1),1)
    def test_goap_rejects_goal_destroying_action(self):
        actions=[('loot',{}, {'ammo':True,'cover':False},1)]
        self.assertIsNone(goap_plan({'ammo':False,'cover':True}, {'ammo':True,'cover':True}, actions))
    def test_goap_reestablishes_deleted_fact_later(self):
        actions=[('loot',{}, {'ammo':True,'cover':False},1),
                 ('cover',{'ammo':True}, {'cover':True},1)]
        self.assertEqual(goap_plan({'ammo':False,'cover':True}, {'ammo':True,'cover':True}, actions), ['loot','cover'])
    def test_goap_zero_cost_cycle_terminates(self):
        actions=[('ab',{'a':True},{'b':True},0),('ba',{'b':True},{'a':True},0)]
        self.assertIsNone(goap_plan({'a':False,'b':False},{'a':True},actions))

if __name__ == '__main__':
    unittest.main(verbosity=2)
