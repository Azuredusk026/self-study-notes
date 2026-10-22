import math
import unittest
from post_models import srgb_decode,srgb_encode,premult_filter,adapt_exposure,reexpose,coc_radius,ssao_weight,soft_bloom,combine_scales,luminance_reinhard

class PostTests(unittest.TestCase):
    def test_srgb_roundtrip_and_midgray(self):
        self.assertAlmostEqual(srgb_decode(.5),.21404114048223255)
        self.assertAlmostEqual(srgb_encode(.5),.7353569830524495)
        for x in (0,.003,.02,.04045,.1,.5,1):
            self.assertAlmostEqual(srgb_encode(srgb_decode(x)),x,delta=3e-8)

    def test_alpha_filtering(self):
        c,a=premult_filter([((1,0,0),1),((0,0,0),0)],[.5,.5])
        self.assertEqual(c,(.5,0,0));self.assertEqual(a,.5)
        self.assertNotEqual(c[0],(.5*1+.5*0)*a)

    def test_exposure_time_and_history(self):
        one=adapt_exposure(1,16,1,1)
        two=adapt_exposure(adapt_exposure(1,16,.5,1),16,.5,1)
        self.assertAlmostEqual(one,two)
        self.assertEqual(reexpose(10,.5,2),40)
        with self.assertRaises(ValueError):reexpose(10,0,2)

    def test_coc_units_and_focus(self):
        self.assertEqual(coc_radius(2,2,.05,2,.036,1920),0)
        self.assertAlmostEqual(coc_radius(1,2,.05,2,.036,1920),-17.094017094017097)
        self.assertGreater(coc_radius(4,2,.05,2,.036,1920),0)
        self.assertAlmostEqual(coc_radius(1,2,.05,4,.036,1920),coc_radius(1,2,.05,2,.036,1920)/2)

    def test_ssao_right_handed_depth(self):
        self.assertEqual(ssao_weight(-2,-2.2,-2.3,.5,.01),0)
        self.assertEqual(ssao_weight(-2,-2.2,-2.1,.5,.01),1)
        self.assertLess(ssao_weight(-2,-2.2,-1,.5,.01),1)

    def test_bloom_knee_and_constant_energy(self):
        self.assertEqual(soft_bloom((0,0,0),1,.5),(0,0,0))
        self.assertAlmostEqual(soft_bloom((1,1,1),1,.5)[0],.125)
        for size in (1,2,5):self.assertAlmostEqual(combine_scales([2]*size,.7),2)

    def test_luminance_mapping_chromatic_ratio(self):
        mapped=luminance_reinhard((10,2,1))
        self.assertAlmostEqual(mapped[0]/mapped[1],5)
        self.assertTrue(mapped[0]>1) # 保持色比并不保证逐通道落在显示色域。
        self.assertEqual(luminance_reinhard((0,0,0)),(0,0,0))

if __name__=='__main__':unittest.main()
