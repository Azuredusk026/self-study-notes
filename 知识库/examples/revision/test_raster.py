import math
import unittest
from raster_models import perspective, depth_pair, box_outside, clip_history, stencil_replace, motion_uv, weighted_oit


class RasterModels(unittest.TestCase):
    def test_motion_divides_each_clip_position(self):
        # Equal clip xy does not imply equal projected position when w changes.
        self.assertEqual(motion_uv((2,0,1,4),(2,0,1,2)),(-.25,0))
        self.assertEqual(motion_uv((0,1,1,2),(0,0,1,2)),(0,-.25))
        self.assertEqual(motion_uv((0,1,1,2),(0,0,1,2),False),(0,.25))

    def test_weighted_oit_empty_and_single_layer(self):
        self.assertEqual(weighted_oit([], (1,.5,0)), (1,.5,0))
        self.assertEqual(weighted_oit([((1,0,0),.5,2)], (1,1,1)), (1,.5,.5))

    def test_weighted_oit_is_order_independent_but_approximate(self):
        layers=[((1,0,0),.5,1),((0,0,1),.5,1)]
        result=weighted_oit(layers,(0,0,0))
        self.assertEqual(result,(.375,0,.375))
        self.assertEqual(result,weighted_oit(list(reversed(layers)),(0,0,0)))
        # Red in front of blue gives .5 red + .25 blue under sorted alpha.
        self.assertNotEqual(result,(.5,0,.25))

    def test_perspective_is_not_screen_average(self):
        self.assertAlmostEqual(perspective((.5,.5,0), (1,2,4), (0,1,0)), 1/3)
        self.assertAlmostEqual(perspective((.2,.3,.5), (2,2,2), (0,1,2)), 1.3)

    def test_depth_round_trip_and_monotonicity(self):
        for reversed_z in (False, True):
            values=[]
            for z in (.1,1,100,1000):
                raw, reconstructed=depth_pair(z,.1,1000,reversed_z)
                self.assertAlmostEqual(reconstructed/z,1,places=10)
                values.append(raw)
            self.assertAlmostEqual(values[0],float(reversed_z))
            self.assertAlmostEqual(values[-1],float(not reversed_z))
            self.assertEqual(values,sorted(values,reverse=reversed_z))

    def test_plane_scale_and_touching_boundary(self):
        # Box centered at x=-2, extent 1 lies outside x>=0.
        for scale in (.01,1,100):
            self.assertTrue(box_outside((scale,0,0),0,(-2,0,0),(1,1,1)))
            self.assertFalse(box_outside((scale,0,0),0,(-1,0,0),(1,1,1)))
        # All eight corners outside agree with the projected-radius test.
        n=(2,-3,4); c=(-5,2,-2); e=(1,2,1)
        corners=[sum(n[i]*(c[i]+sgn[i]*e[i]) for i in range(3)) for sgn in
                 ((x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1))]
        self.assertEqual(box_outside(n,0,c,e),max(corners)<0)

    def test_clip_stays_inside_and_handles_flat_box(self):
        self.assertEqual(clip_history((.2,.5,.8),(0,0,0),(1,1,1)),(.2,.5,.8))
        self.assertEqual(clip_history((5,-2,3),(1,1,1),(1,1,1)),(1,1,1))
        value=clip_history((2,1,.5),(0,0,0),(1,1,1))
        self.assertEqual(value,(1,2/3,.5))

    def test_stencil_does_not_destroy_other_owners(self):
        for old in range(256):
            result=stencil_replace(old,0x20,0xF0)
            self.assertEqual(result&0xF0,0x20)
            self.assertEqual(result&0x0F,old&0x0F)
        self.assertEqual([s for s in (0x10,0x20,0x30,0x80) if (0x30&0xF0)>=(s&0xF0)],
                         [0x10,0x20,0x30])


if __name__=='__main__':
    unittest.main()
