import unittest
from reference import bake, evaluate
class Tests(unittest.TestCase):
 def test_bracket(self):
  self.assertEqual(bake([0,.25,.5,.75,1],[1,1,1,0,0]),(.625,.25))
 def test_reentry_rejected(self):
  with self.assertRaises(ValueError):bake([0,.5,1],[1,0,1])
 def test_vertical_is_azimuth_independent(self):
  self.assertAlmostEqual(evaluate((1e-8,1,0),(.2,.8),.4,.1),evaluate((-1e-8,1,0),(.2,.8),.4,.1),places=5)
 def test_far_from_vertical(self):
  self.assertAlmostEqual(evaluate((1,0,0),(.2,.8),.4,.1),1)
 def test_endpoints(self):
  self.assertEqual(bake([0,.5,1],[1,1,1]),(1.0,0.0))
  self.assertEqual(bake([0,.5,1],[0,0,0]),(0.0,0.0))
if __name__=='__main__':unittest.main()
