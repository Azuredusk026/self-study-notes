import unittest
from clock_reference import slew_anchor

class ClockContinuity(unittest.TestCase):
    def test_negative_phase_error_does_not_move_current_anchor(self):
        anchor, rate, frequency = slew_anchor(100, 99.99, 1, 1, 1)
        self.assertEqual(anchor, 100)
        self.assertAlmostEqual(rate, .99)
    def test_positive_phase_error_changes_future_rate_only(self):
        anchor, rate, frequency = slew_anchor(100,100.2,1,1,1)
        self.assertEqual(anchor,100)
        self.assertAlmostEqual(anchor+rate*.5,100.505)
    def test_maximum_negative_slew_keeps_time_forward(self):
        anchor, rate, frequency = slew_anchor(100, 90, .9998, .9998, 1)
        self.assertAlmostEqual(rate,.9898)
        self.assertGreater(anchor+rate*.001,100)
    def test_physical_frequency_is_limited_separately(self):
        anchor, rate, frequency = slew_anchor(100,100,1,1.0002,.1)
        self.assertAlmostEqual(frequency,1.000002)
        self.assertAlmostEqual(rate,1.000002)

if __name__ == '__main__': unittest.main()
