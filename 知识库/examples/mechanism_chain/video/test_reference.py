import unittest
from reference import exposure_gain, project_clean, ddim_update, choose_steps, apply_gain, next_confidence, sample_history

class ChainTests(unittest.TestCase):
    def test_rejected_tap_is_not_diluted_by_high_confidence_neighbors(self):
        self.assertIsNone(sample_history([.2,.9],[.9,.1],[1,0]))
        self.assertAlmostEqual(sample_history([.2,.9],[1,0],[1,0]),.2)
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

class AnchorTests(unittest.TestCase):
    def test_fresh_unapproved_generation_is_not_an_anchor(self):
        from reference import history_state
        self.assertEqual(history_state(.9,.9,.9,False,True), (1,0))
    def test_content_failure_rejects_both_kinds_of_confidence(self):
        from reference import history_state
        self.assertEqual(history_state(1,1,1,True,False), (0,0))
    def test_accepted_history_keeps_anchor_chain_separate(self):
        from reference import history_state
        q,a = history_state(1,.9,.9,True,True)
        self.assertAlmostEqual(q,.9)
        self.assertAlmostEqual(a,.81)
    def test_approved_keyframe_starts_both_histories(self):
        from reference import history_state
        self.assertEqual(history_state(0,0,0,False,True,approved=True), (1,1))
    def test_local_confidence_cannot_reactivate_lost_anchor(self):
        from reference import history_state,anchor_weights
        q,a = history_state(1,0,.9,True,True)
        self.assertAlmostEqual(q,.9)
        self.assertEqual(a,0)
        self.assertIsNone(anchor_weights(4,6,a,0))
    def test_fusion_ignores_anchor_below_acceptance_threshold(self):
        from reference import anchor_weights
        self.assertEqual(anchor_weights(4,6,1,.79), (1,0))
    def test_fusion_normalizes_time_times_anchor(self):
        from reference import anchor_weights
        l,r=anchor_weights(4,6,1,.8)
        self.assertAlmostEqual(l, .6521739130434783)
        self.assertAlmostEqual(r, .3478260869565218)

if __name__ == '__main__': unittest.main()
