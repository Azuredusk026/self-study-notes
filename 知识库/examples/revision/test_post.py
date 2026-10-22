import math
import unittest
import post_models
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

    def test_exposure_rejects_nonfinite_parameters(self):
        for previous,current in ((float('nan'),2),(.5,float('inf'))):
            with self.subTest(previous=previous,current=current),self.assertRaises(ValueError):
                reexpose(10,previous,current)
        for args in ((1,16,float('nan'),1),(1,float('inf'),1,1),(1,16,1,float('inf'))):
            with self.subTest(args=args),self.assertRaises(ValueError):adapt_exposure(*args)

    def test_coc_unit_conversion_and_invalid_parameters(self):
        self.assertAlmostEqual(coc_radius(1000,2000,50,2,36,1920),coc_radius(1,2,.05,2,.036,1920))
        for args in ((1,2,0,2,.036,1920),(1,2,.05,2,.036,0),(1,2,float('nan'),2,.036,1920)):
            with self.subTest(args=args),self.assertRaises(ValueError):coc_radius(*args)

    def test_ssao_length_scale_invariance(self):
        args=(-2,-2.2,-2.1,.5,.01)
        self.assertAlmostEqual(ssao_weight(*args),ssao_weight(*(x*1e-6 for x in args)))

    def test_bloom_preexposure_scale_invariance(self):
        scale=1e-8
        original=soft_bloom((1,1,1),1,.5)
        scaled=soft_bloom((scale,scale,scale),scale,.5*scale)
        for expected,actual in zip(original,scaled):
            self.assertAlmostEqual(actual,expected*scale,delta=1e-20)
        with self.assertRaises(ValueError):soft_bloom((0,0,0),0,1)

    def test_motion_gather_recovers_translated_bright_point(self):
        # A point moves from u=.5 to .6. A trailing half-frame shutter covers [.55,.6].
        # At target .575, the midpoint sample must read the current point at .6.
        sample=post_models.motion_blur_uv((.575,.4),(-.1,0),1/120,1/60,0,1)
        self.assertAlmostEqual(sample[0],.6);self.assertEqual(sample[1],.4)
        self.assertAlmostEqual(.575+(-.1)*.5*.5,.55) # The opposite sign samples empty space.
        self.assertEqual(post_models.motion_blur_uv((.575,.4),(-.1,0),0,1/60,0,1),(.575,.4))
        with self.assertRaises(ValueError):post_models.motion_blur_uv((.5,.4),(-.1,0),.01,0,0,1)

if __name__=='__main__':unittest.main()
