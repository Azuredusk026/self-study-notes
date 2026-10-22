"""PBR、环境积分与次表面散射的数值边界检查。"""
import math
import unittest
from lighting_models import ggx_d, specular, integrate_lut, rnm, annulus_energy, projected_radius, preintegrated_diffuse


class LightingTests(unittest.TestCase):
    def test_ndf_projected_area(self):
        for alpha in (0.2, 0.5, 1.0):
            n = 50000
            integral = sum(ggx_d((i + .5) / n, alpha) * (i + .5) / n for i in range(n)) * 2 * math.pi / n
            self.assertAlmostEqual(integral, 1, delta=1e-6)

    def test_reciprocity_and_backface(self):
        v = (0.6, 0, 0.8)
        l = (0, math.sqrt(.75), .5)
        self.assertAlmostEqual(specular(v, l, .4, .04), specular(l, v, .4, .04))
        self.assertEqual(specular(v, (0, 0, -1), .4, .04), 0)

    def test_single_scattering_white_furnace(self):
        n = 20000
        energy = sum(specular((0, 0, 1), (math.sqrt(1-((i+.5)/n)**2), 0, (i+.5)/n), 1, 1) * (i+.5)/n for i in range(n)) * 2 * math.pi/n
        self.assertAlmostEqual(energy, 1-math.log(2), delta=1e-8)
        self.assertLess(energy, 1)

    def test_lut_matches_independent_quadrature(self):
        a, b = integrate_lut(1, 1, 32768)
        self.assertAlmostEqual(a + b, 1-math.log(2), delta=1e-4)
        self.assertGreaterEqual(a, 0)
        self.assertGreaterEqual(b, 0)

    def test_rnm_matches_rotation(self):
        base = (.6, 0, .8)
        detail = (0, .8, .6)
        # 绕 Y 轴旋转，cos=.8、sin=.6，将 +Z 转到 base。
        expected = (.36, .8, .48)
        for actual, wanted in zip(rnm(base, detail), expected):
            self.assertAlmostEqual(actual, wanted)
        for a, b in zip(rnm(base, (0, 0, 1)), base):
            self.assertAlmostEqual(a, b)
        for a, b in zip(rnm((0, 0, 1), detail), detail):
            self.assertAlmostEqual(a, b)

    def test_profile_center_and_energy(self):
        for d in (.001, .01, 1):
            self.assertEqual(annulus_energy(0, 0, d, .7), 0)
            self.assertAlmostEqual(annulus_energy(0, 100*d, d, .7), .7)
            parts = sum(annulus_energy(i*d, (i+1)*d, d, .7) for i in range(100))
            self.assertAlmostEqual(parts, .7)

    def test_projection_units(self):
        r = projected_radius(.01, 1, math.pi/2, 1080)
        self.assertAlmostEqual(r, 5.4)
        self.assertAlmostEqual(projected_radius(.01, 2, math.pi/2, 1080), r/2)


class PreintegrationTests(unittest.TestCase):
    def test_flat_profile_recovers_lambert(self):
        for mu in (-1, -.5, 0, .25, 1):
            self.assertAlmostEqual(preintegrated_diffuse(mu, 0), max(mu, 0))

    def test_horizon_and_radius(self):
        self.assertEqual(preintegrated_diffuse(0, 0), 0)
        self.assertGreater(preintegrated_diffuse(0, .2), preintegrated_diffuse(0, .1))
        self.assertGreater(preintegrated_diffuse(0, .1), 0)

    def test_normal_incidence_matches_gaussian_characteristic(self):
        # q=.2 在截断区间上余弦为正；完整高斯的解析值为 exp(-q²/2)。
        self.assertAlmostEqual(preintegrated_diffuse(1, .2), math.exp(-.2**2/2), delta=1e-4)

    def test_bounds_convergence_and_invalid_input(self):
        for mu in (-1, -.2, 0, .7, 1):
            value=preintegrated_diffuse(mu, .25)
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 1)
            self.assertAlmostEqual(value, preintegrated_diffuse(mu, .25, 4096), delta=1e-6)
        for mu, q in ((1.1,.2),(0,-.1),(float('nan'),.1)):
            with self.assertRaises(ValueError): preintegrated_diffuse(mu,q)
        with self.assertRaises(ValueError): preintegrated_diffuse(0,.1,0)

if __name__ == '__main__':
    unittest.main()
