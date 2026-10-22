import math
import unittest
from gi_models import probe_weights, box_direction, moment_visibility, history_update, polygon_cosine, clip_horizon, pcss_radius_uv

class GITests(unittest.TestCase):
    def test_probe_reproduces_affine_field(self):
        t=(.2,.3,.7); weights=probe_weights(t)
        self.assertAlmostEqual(sum(weights),1)
        values=[2*(i&1)+3*((i>>1)&1)-((i>>2)&1)+4 for i in range(8)]
        self.assertAlmostEqual(sum(w*v for w,v in zip(weights,values)),2*t[0]+3*t[1]-t[2]+4)
        self.assertEqual(probe_weights((0,0,0)),[1,0,0,0,0,0,0,0])

    def test_box_parallel_and_center(self):
        bmin=(-1,-1,-1);bmax=(1,1,1)
        self.assertEqual(box_direction((0,0,0),(1,0,0),bmin,bmax,(0,0,0)),(1,0,0))
        d=box_direction((.5,0,0),(0,0,1),bmin,bmax,(0,0,0))
        self.assertAlmostEqual(d[0]/d[2],.5)
        self.assertIsNone(box_direction((2,0,0),(0,0,1),bmin,bmax,(0,0,0)))
        self.assertIsNone(box_direction((0,0,0),(0,0,0),bmin,bmax,(0,0,0)))

    def test_moment_bound_is_not_visibility(self):
        self.assertEqual(moment_visibility(4,20,3),1)
        self.assertAlmostEqual(moment_visibility(4,20,5),.8)
        # 实际深度只可能为 2 或 6，等概率；5 处实际可见性为 .5。
        self.assertGreater(moment_visibility(4,20,5),.5)
        self.assertEqual(moment_visibility(4,16,5),0)

    def test_temporal_delay_and_reset(self):
        value=0
        for _ in range(10):value=history_update(value,1,.9)
        self.assertAlmostEqual(value,1-.9**10)
        self.assertEqual(history_update(9,1,.9,False),1)

    def test_polygon_matches_area_quadrature(self):
        corners=[(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
        n=240; width=2/n
        expected=sum(1/(math.pi*(1+(-1+(x+.5)*width)**2+(-1+(y+.5)*width)**2)**2)*width**2 for y in range(n) for x in range(n))
        self.assertAlmostEqual(polygon_cosine(corners),expected,delta=4e-6)
        self.assertAlmostEqual(polygon_cosine([tuple(3*x for x in p) for p in corners]),polygon_cosine(corners))

    def test_horizon_clipping(self):
        self.assertEqual(polygon_cosine([(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1)]),0)
        source=[(-1,1,-1),(1,1,-1),(1,1,1),(-1,1,1)]
        clipped=clip_horizon(source)
        self.assertEqual(len(clipped),4)
        self.assertTrue(all(p[2]>=0 for p in clipped))
        self.assertAlmostEqual(polygon_cosine(source),polygon_cosine(clipped))

    def test_pcss_width_to_radius(self):
        self.assertEqual(pcss_radius_uv(.2,2,2,10),0)
        self.assertAlmostEqual(pcss_radius_uv(.2,2,4,10),.01)
        self.assertAlmostEqual(pcss_radius_uv(.2,2,4,20),.005)

if __name__=='__main__':unittest.main()
