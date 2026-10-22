"""Hand-derived counterexamples for Deferred Rendering's data contracts."""
import math
import unittest
from reference import reconstruct, transform_point, transform_direction, shade, over, resolve


class Contracts(unittest.TestCase):
    def test_depth_reconstruction_uses_top_left_pixel_coordinates(self):
        identity = ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1))
        self.assertEqual(reconstruct((0.25,0.25),0.5,identity),(-0.5,0.5,0.5))

    def test_position_divides_homogeneous_w(self):
        inverse = ((1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,1,1))
        self.assertEqual(reconstruct((0.5,0.5),1,inverse),(0,0,0.5))

    def test_light_translation_does_not_translate_normal(self):
        view = ((0,-1,0,-2),(1,0,0,3),(0,0,1,0),(0,0,0,1))
        self.assertEqual(transform_point(view,(1,0,0)),(-2,4,0))
        self.assertEqual(transform_direction(view,(1,0,0)),(0,1,0))

    def test_same_rotation_preserves_lambert_but_mixed_space_does_not(self):
        self.assertAlmostEqual(shade((0,1,0),(0,2,0),0),1/math.pi)
        self.assertEqual(shade((1,0,0),(0,2,0),0),0)

    def test_discrete_models_dispatch_before_shading(self):
        self.assertAlmostEqual(shade((0,0,1),(0,0,1),0),1/math.pi)
        self.assertEqual(shade((0,0,1),(0,0,1),1),1)
        with self.assertRaises(ValueError):
            shade((0,0,1),(0,0,1),7)

    def test_transparent_order_changes_result(self):
        background=(0,0,1)
        # Far green then near red, both alpha = 0.5, already premultiplied.
        self.assertEqual(over((0.5,0,0),0.5,over((0,0.5,0),0.5,background)),(0.5,0.25,0.25))
        self.assertEqual(over((0,0.5,0),0.5,over((0.5,0,0),0.5,background)),(0.25,0.5,0.25))

    def test_average_normals_before_shading_creates_false_surface(self):
        colors=[shade((0,0,1),(0,0,1),0),shade((0,0,-1),(0,0,1),0)]
        self.assertAlmostEqual(resolve(colors),1/(2*math.pi))
        # Averaging these normals gives zero, not a valid replacement surface.
        with self.assertRaises(ValueError):
            shade((0,0,0),(0,0,1),0)

    def test_uncovered_msaa_samples_keep_background(self):
        self.assertEqual(resolve([1,1,0,0]),0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
