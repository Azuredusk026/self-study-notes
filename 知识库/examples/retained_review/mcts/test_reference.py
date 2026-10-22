import unittest
try:
    from reference import search
except ImportError:
    search = None
class SearchTests(unittest.TestCase):
    def test_complete_game_and_backpropagation(self):
        self.assertIsNotNone(search, '完整搜索实现尚缺失')
        root, trace = search(4, 120, 7)
        self.assertEqual(root.visits,120)
        self.assertEqual(sum(c.visits for c in root.children),120)
        self.assertEqual(max(root.children,key=lambda c:c.visits).action,1)
        self.assertEqual(trace[0]['path'],[1])
    def test_terminal_and_repeatability(self):
        self.assertIsNotNone(search, '完整搜索实现尚缺失')
        a,ta=search(4,120,7); b,tb=search(4,120,7)
        self.assertEqual(ta,tb)
        r,t=search(0,3,7)
        self.assertEqual(r.total,-3)
if __name__=='__main__': unittest.main()
