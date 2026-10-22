import unittest
from reference import damage, components, cluster
class Tests(unittest.TestCase):
 def test_radial_damage_budget(self):
  self.assertEqual(damage([10,4],[0,1],2,6),[6,2])
 def test_repeat_damage_breaks(self):
  self.assertEqual(damage([6,2],[0,1],2,6),[2,0])
 def test_support_after_bridge_break(self):
  self.assertEqual(components(3,[(0,1)],{0}),[(frozenset({0,1}),True),(frozenset({2}),False)])
 def test_cycle_keeps_support(self):
  self.assertEqual(components(3,[(0,1),(1,2)],{0}),[(frozenset({0,1,2}),True)])
 def test_mass_center_inertia_and_velocity(self):
  m,c,i,v=cluster([1,3],[0,2],[1/6,1/2],0,1,2)
  self.assertEqual((m,c,i,v),(4,1.5,11/3,4))
 def test_single_body_has_no_offset(self):
  self.assertEqual(cluster([2],[3],[.5],3,7,4),(2,3,.5,7))
if __name__=='__main__':unittest.main()
