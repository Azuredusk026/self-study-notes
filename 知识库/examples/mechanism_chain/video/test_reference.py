import unittest
from reference import exposure_gain, project_clean, ddim_update, choose_steps, apply_gain, next_confidence

class ChainTests(unittest.TestCase):
    def test_invalid_history_never_replaces_revealed_pixel(self):
        result = project_clean([.2,.4], [.9,.8], [0,1], .75)
        self.assertEqual(result[0], .2)
        self.assertAlmostEqual(result[1], .7)
    def test_history_gain_tracks_only_drift(self):
        self.assertAlmostEqual(exposure_gain([.2,.4,.6],[.1,.2,.3],[1,1,1],1), 1.05)
    def test_no_eligible_samples_keeps_gain(self):
        self.assertEqual(exposure_gain([.2],[.1],[0],1.2),1.2)
    def test_exposure_estimator_is_robust_to_one_outlier(self):
        self.assertAlmostEqual(exposure_gain([.2,.4,.9],[.2,.4,.1],[1,1,1],1),1)
    def test_projection_uses_next_noise_level(self):
        self.assertAlmostEqual(ddim_update(2,1,.64),2.2)
    def test_final_step_is_clean(self):
        self.assertEqual(ddim_update(2,999,1),2)
    def test_img2img_strength_selects_tail(self):
        self.assertEqual(choose_steps([900,800,700,600,500,400,300,200,100,0],.4),[300,200,100,0])
    def test_empty_strength_is_rejected(self):
        with self.assertRaises(ValueError): choose_steps([9,8],.1)
    def test_lighting_changed_object_is_excluded_from_gain_application(self):
        result = apply_gain([.2,.6],1.05,[1,0])
        self.assertAlmostEqual(result[0],.21)
        self.assertEqual(result[1],.6)
    def test_content_rejection_survives_new_generation_confidence_reset(self):
        self.assertEqual(next_confidence([0,1],[0,0],[.2,.2]),[0,1])

if __name__ == '__main__': unittest.main()
