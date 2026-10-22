import math
import unittest
from reference import (texture_lod, bilinear, mip_bytes, stream_targets, vt_address,
                       pom_line, select_lod, height_normal, billboard_right,
                       flatten_corners, cache_misses, quadric_error, phong_point,
                       ellipsoid_normal, smooth_step)


class TextureGeometry(unittest.TestCase):
    def test_lod_uses_texel_units_and_both_dimensions(self):
        self.assertAlmostEqual(texture_lod((1/256,0),(0,1/128),(1024,512)),2)
        self.assertAlmostEqual(texture_lod((1/1024,0),(0,1/512),(1024,512)),0)
        self.assertAlmostEqual(texture_lod((4/256,0),(0,4/128),(1024,512)),4)

    def test_bilinear_centers_edges_and_clamp(self):
        pixels=((0,2),(4,6))
        self.assertEqual(bilinear(pixels,(.25,.25)),0)
        self.assertEqual(bilinear(pixels,(.5,.5)),3)
        self.assertEqual(bilinear(pixels,(-1,2)),4)

    def test_block_rounding_and_rectangular_tail(self):
        self.assertEqual(mip_bytes(5,3,4,4,8),[16,8,8])
        self.assertEqual(sum(mip_bytes(1024,1024,4,4,8)),699064)
        self.assertEqual(sum(mip_bytes(8,1,1,1,1)),15)

    def test_streaming_budget_and_fallback(self):
        levels=[[64,16,4,1],[64,16,4,1]]
        self.assertEqual(stream_targets(levels,[0,0],[10,1],22),[1,3])
        self.assertEqual(stream_targets(levels,[2,1],[1,1],170),[2,1])
        with self.assertRaises(ValueError): stream_targets(levels,[0,0],[1,1],1)

    def test_virtual_page_center_and_ancestor_remap(self):
        wanted,found,uv=vt_address((.5625,.0625),0,2,4,1,(12,12),{(0,1,0):(1,0)})
        self.assertEqual(wanted,found)
        self.assertEqual(uv,(7.5/12,1.5/12))
        wanted,found,uv=vt_address((.75,.25),0,2,4,1,(12,12),{(1,0,0):(0,1)})
        self.assertEqual(wanted,(0,1,0)); self.assertEqual(found,(1,0,0))
        self.assertEqual(uv,(4/12,8/12))
        with self.assertRaises(ValueError): vt_address((.5,.5),0,2,4,1,(12,12),{})

    def test_virtual_non_power_of_two_grid_rejected(self):
        with self.assertRaisesRegex(ValueError, 'power of two'):
            vt_address((.5,.5),0,3,4,1,(12,12),{(1,0,0):(0,0)})

    def test_virtual_tail_outside_model_is_explicit(self):
        with self.assertRaisesRegex(ValueError, 'mip range'):
            vt_address((.5,.5),2,2,4,1,(12,12),{(1,0,0):(0,0)})

    def test_pom_top_surface_and_constant_depth(self):
        self.assertEqual(pom_line(.6,.2,8,lambda u:0),(.6,0))
        u,t=pom_line(.6,.2,8,lambda u:.3)
        self.assertAlmostEqual(t,.3); self.assertAlmostEqual(u,.54)

    def test_pom_linear_intersection_and_budget(self):
        u,t=pom_line(.6,.2,16,lambda u:.2+.2*u)
        self.assertAlmostEqual(t,.32/1.04)
        self.assertAlmostEqual(u,.6-.2*t)

    def test_lod_hysteresis_and_large_jump(self):
        self.assertEqual(select_lod(.19,0,[.2,.05],.02),0)
        self.assertEqual(select_lod(.17,0,[.2,.05],.02),1)
        self.assertEqual(select_lod(.21,1,[.2,.05],.02),1)
        self.assertEqual(select_lod(.23,1,[.2,.05],.02),0)
        self.assertEqual(select_lod(.01,0,[.2,.05],.02),2)

    def test_height_normal_respects_world_spacing(self):
        # h(x,z)=2x+3z; spacing x=2,z=4.
        n=height_normal(-4,4,-12,12,2,4)
        expected=(-2/math.sqrt(14),1/math.sqrt(14),-3/math.sqrt(14))
        for a,b in zip(n,expected): self.assertAlmostEqual(a,b)

    def test_billboard_overhead_fallback_is_orthogonal(self):
        self.assertEqual(billboard_right((0,5,0),(0,1,0),(1,1,0)),(1,0,0))
        self.assertEqual(billboard_right((0,0,5),(0,1,0),(1,0,0)),(1,0,0))

    def test_vertex_identity_includes_uv_seam(self):
        a=((0,0,0),(0,0)); b=((1,0,0),(1,0)); seam=((0,0,0),(1,1))
        vertices,indices=flatten_corners([a,b,a,seam])
        self.assertEqual(len(vertices),3); self.assertEqual(indices,[0,1,0,2])
        self.assertEqual(cache_misses([0,1,2,2,1,3],3),4)

    def test_quadric_plane_error(self):
        self.assertEqual(quadric_error((2,3,4),[(1,0,0,-1),(0,0,1,-2)]),5)

    def test_phong_preserves_vertices_and_coplanar_surface(self):
        p=((0,0,0),(1,0,0),(0,1,0)); n=((0,0,1),)*3
        self.assertEqual(phong_point(p,n,(.2,.3,.5),1),(.3,.5,0))
        tilted=((1/math.sqrt(2),0,1/math.sqrt(2)),(0,0,1),(0,0,1))
        self.assertEqual(phong_point(p,tilted,(1,0,0),1),p[0])
        self.assertNotEqual(phong_point(p,tilted,(.5,.5,0),1),(.5,0,0))

    def test_wrapped_normal_ellipsoid_metric(self):
        n=ellipsoid_normal((2,1,0),(0,0,0),(2,1,1))
        self.assertAlmostEqual(n[1]/n[0],2)
        self.assertEqual(ellipsoid_normal((0,0,0),(0,0,0),(2,1,1)),(0,1,0))

    def test_smoothing_is_simultaneous_and_preserves_fixed_boundary(self):
        p=((0.,0,0),(2.,0,0),(4.,0,0)); neighbours=((1,),(0,2),(1,))
        self.assertEqual(smooth_step(p,neighbours,.5,{0}),[(0.,0,0),(2.,0,0),(3.,0,0)])


if __name__=='__main__': unittest.main()
