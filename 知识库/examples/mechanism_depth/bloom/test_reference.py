import unittest
from reference import down2, tent_up, pyramid
class BloomTests(unittest.TestCase):
    def test_constant(self):
        self.assertTrue(all(abs(v-4)<1e-10 for row in pyramid([[4.]*16 for _ in range(16)],3,.8) for v in row))
    def test_impulse(self):
        image=[[0.]*16 for _ in range(16)]; image[8][8]=16
        self.assertEqual(down2(image)[4][4],4)
        self.assertEqual(down2(down2(image))[2][2],1)
        fine=pyramid(image,2,0); wide=pyramid(image,2,.8)
        self.assertEqual(fine[5][5],0)
        self.assertGreater(wide[5][5],0)
        self.assertLess(wide[8][8],16)
    def test_tent(self):
        image=[[0.]*9 for _ in range(9)];image[4][4]=16
        result=tent_up(image,9,9)
        self.assertAlmostEqual(result[4][4],4)
        self.assertAlmostEqual(result[4][5],2)
        self.assertAlmostEqual(result[5][5],1)
    def test_odd_rejected(self):
        with self.assertRaises(ValueError): down2([[1]*3 for _ in range(4)])
    def test_scales(self):
        self.assertAlmostEqual(.2+.8*.2+.8**2,1)
