"""CPU contracts: CDF boundaries, SH normalization, noise continuity."""
import math
import unittest
import math_models as model


class MathChecks(unittest.TestCase):
    def test_cdf_skips_empty_bins(self):
        self.assertEqual(model.draw_cdf([0, 1, 0, 3, 0], 0), (1, .25))
        self.assertEqual(model.draw_cdf([0, 1, 0, 3, 0], .25), (3, .75))
        self.assertEqual(model.draw_cdf([0, 1, 0, 3, 0], math.nextafter(1, 0)), (3, .75))

    def test_cdf_invalid_input(self):
        for weights, u in [([], 0), ([1], 1), ([-1, 2], .2), ([math.inf], .5)]:
            with self.assertRaises(ValueError):
                model.draw_cdf(weights, u)
        self.assertEqual(model.draw_cdf([0, 0], .75), (1, .5))

    def test_sh_constant_environment(self):
        coefficients = [2 * math.sqrt(4 * math.pi)] + [0] * 8
        for n in [(1, 0, 0), (0, -1, 0), (0, 0, 1)]:
            self.assertAlmostEqual(model.sh_irradiance(coefficients, n), 2 * math.pi)

    def test_sh_linear_environment(self):
        # L(w)=1+w.z gives E(n)=pi+(2*pi/3)*n.z.
        c = [math.sqrt(4 * math.pi), 0, math.sqrt(4 * math.pi / 3)] + [0] * 6
        self.assertAlmostEqual(model.sh_irradiance(c, (0, 0, 1)), 5 * math.pi / 3)
        self.assertAlmostEqual(model.sh_irradiance(c, (0, 0, -1)), math.pi / 3)

    def test_noise_integer_and_boundary(self):
        for i in [-2, -1, 0, 1, 2]:
            self.assertAlmostEqual(model.gradient_noise(i, 7), 0)
            self.assertAlmostEqual(model.gradient_noise(i - 1e-7, 7),
                                   model.gradient_noise(i + 1e-7, 7), places=5)
        self.assertEqual(model.gradient_noise(-.25, 7), model.gradient_noise(-.25, 7))
        self.assertNotEqual(model.gradient_noise(.25, 7), 0)


if __name__ == '__main__':
    unittest.main()
