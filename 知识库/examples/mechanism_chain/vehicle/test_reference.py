import unittest, math
from reference import suspension,tire,spin,wheel_step,contact_geometry,lock_impulse_limits
class WheelMechanisms(unittest.TestCase):
    def test_parking_low_nonzero_spin_still_requires_stop_impulse(self):
        lo,hi=lock_impulse_limits(.2,0,1,1,.1,.3)
        self.assertAlmostEqual(lo,1/3)
        self.assertAlmostEqual(hi,1)
        self.assertFalse(lo<=0<=hi)
        self.assertAlmostEqual(spin(.2,0,1,0,.3,1,.1),.1)
    def test_camber_distinguishes_round_wheel_and_sphere_envelope(self):
        circular = contact_geometry(.8,.3,.8,.6,False)
        sphere = contact_geometry(.8,.3,.8,.6,True)
        self.assertAlmostEqual(circular['length'],.5)
        self.assertAlmostEqual(circular['lever'],.3)
        self.assertAlmostEqual(sphere['length'],.425)
        self.assertAlmostEqual(sphere['lever'],.24)
    # Omitting radius, normal projection, combined load, or reaction breaks these outputs.
    def test_flat_contact_to_load(self):
        s=suspension(.8,.3,.6,.2,.8,20000,2000,1,-.2)
        self.assertAlmostEqual(s['length'],.5);self.assertAlmostEqual(s['compression'],.1);self.assertAlmostEqual(s['spring'],2400);self.assertAlmostEqual(s['load'],2400)
    def test_slope_geometry_and_load_projection(self):
        s=suspension(.8,.24,.6,.2,.8,20000,0,.8,0)
        self.assertAlmostEqual(s['length'],.5);self.assertAlmostEqual(s['load'],1600)
    def test_airborne_has_no_contact_force(self):
        self.assertEqual(suspension(None,.3,.6,.2,.8,20000,2000,1,0)['load'],0)
        self.assertEqual(tire(5,1,30,.3,0,.8,10000,10000),(0,0))
    def test_raw_lateral_and_longitudinal_share_budget(self):
        fx,fy=tire(5,5*math.tan(.1),20,.3,2000,1,10000,10000)
        # kappa=.2 -> 2000, alpha=.1 -> -1000, clipped to norm 2000.
        self.assertAlmostEqual(fx,1788.8543819998);self.assertAlmostEqual(fy,-894.4271909999)
    def test_brake_stops_both_directions_without_reversal(self):
        self.assertEqual(spin(1,0,20,0,.3,1,.1),0);self.assertEqual(spin(-1,0,20,0,.3,1,.1),0)
        self.assertAlmostEqual(spin(0,30,20,0,.3,1,.1),1)
    def test_one_step_force_and_spin_use_same_reaction(self):
        out=wheel_step(.8,5,0,20,0,0,.01,1000)
        # x=.1 -> Fz2000; kappa=.2 -> Fx2000; omega loses Fx*r*dt/I=6.
        self.assertAlmostEqual(out['load'],2000);self.assertAlmostEqual(out['fx'],2000);self.assertAlmostEqual(out['omega'],14);self.assertAlmostEqual(out['dv'],.02)
if __name__=='__main__':unittest.main()
