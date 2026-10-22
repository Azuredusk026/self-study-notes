import math, cmath, unittest
from reference import evolve, inverse, derivative, transmittance, segment, uv, unmap, phase, optical_depth, build_lut, lookup_lut
class MechanismTests(unittest.TestCase):
 def test_hermitian(self):
  h=evolve({1:1+2j,-1:3-1j},.7,2)
  self.assertAlmostEqual(abs(h[-1]-h[1].conjugate()),0)
 def test_inverse_cosine(self):
  self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(inverse({1:.5,-1:.5},4),[1,0,-1,0])))
 def test_spectral_derivative(self):
  self.assertAlmostEqual(derivative({1:.5,-1:.5},4,1),-math.pi/2)
 def test_constant_atmosphere(self):
  self.assertAlmostEqual(transmittance(.1,10),math.exp(-1))
 def test_segment_subdivision(self):
  a,t=segment(.1,.04,10,1)
  b,u=segment(.1,.04,5,1)
  self.assertAlmostEqual(a,b+u*b); self.assertAlmostEqual(t,u*u)
 def test_zero_extinction(self):
  self.assertEqual(segment(0,.04,10,1),(0.4,1.0))
 def test_lut_mapping(self):
  for r,mu in [(1,1),(1.5,0),(1.5,-.5),(2,1)]:
   u,v=uv(r,mu,1,2,32,16); rr,mm=unmap(u,v,1,2,32,16)
   self.assertAlmostEqual(rr,r); self.assertAlmostEqual(mm,mu)
 def test_vertical_density_integral(self):
  tau=optical_depth(1,1,1,2,.3,.4,2048)
  self.assertAlmostEqual(tau,.3*.4*(1-math.exp(-1/.4)),places=7)
 def test_lut_node_lookup(self):
  lut=build_lut(1,2,.3,.4,9,5,128)
  u,v=.5/9+3/8*(1-1/9),.5/5+2/4*(1-1/5)
  r,mu=unmap(u,v,1,2,9,5)
  self.assertAlmostEqual(lookup_lut(lut,r,mu,1,2),math.exp(-optical_depth(r,mu,1,2,.3,.4,128)))
 def test_ground_shadow(self):
  self.assertEqual(optical_depth(1.1,-1,1,2,.3,.4,64),math.inf)
 def test_phase_forward(self):
  self.assertGreater(phase(.8,1),phase(.8,-1))
if __name__=='__main__': unittest.main()
