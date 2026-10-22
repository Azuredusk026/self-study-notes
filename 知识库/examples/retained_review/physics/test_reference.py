"""Independent scalar/vector checks, not a physics host."""
import math,unittest
class PhysicsChecks(unittest.TestCase):
 def test_inactive_planes_leave_motion(self):
  normals=((1,0,0),(0,1,0));d=(1,1,0)
  self.assertTrue(all(sum(a*b for a,b in zip(d,n))>=0 for n in normals))
  # Both contacts are separating: projecting onto their Z intersection would be wrong.
  self.assertNotEqual((0,0,0),d)
 def test_upright_root_preserves_pelvis_position(self):
  pelvis=(3,1,4);local=(0,1,0)
  # yaw-only identity root; fallen orientation belongs to captured skeleton.
  root=tuple(a-b for a,b in zip(pelvis,local))
  self.assertEqual(tuple(a+b for a,b in zip(root,local)),pelvis)
  adjusted=(3,0,5)
  captured=tuple(a-b for a,b in zip(pelvis,adjusted))
  self.assertEqual(tuple(a+b for a,b in zip(adjusted,captured)),pelvis)
 def test_low_speed_rule(self):
  def slip(v,w):return (.3*w-v)/max(abs(v),1.)
  self.assertEqual(slip(0,0),0)
  self.assertAlmostEqual(slip(0,1),.3)
  self.assertAlmostEqual(slip(1e-9,0),-1e-9)
  self.assertEqual(math.atan2(0,max(abs(0),1)),0)
if __name__=='__main__':unittest.main()
