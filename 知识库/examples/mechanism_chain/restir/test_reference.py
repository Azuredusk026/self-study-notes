import itertools
import unittest
from reference import merge_outcomes


class Correction(unittest.TestCase):
    def average(self, mode, neighbor_target):
        total=0.0
        for current,neighbor in itertools.product((0,1),repeat=2):
            pools=[(current,2.0,1),(neighbor if neighbor_target[neighbor]>0 else None,
                                     2.0 if neighbor_target[neighbor]>0 else 0.0,1)]
            for y,weight,probability,origin in merge_outcomes(pools,[1,1],[[1,1],neighbor_target],mode):
                total+=0.25*weight*probability
        return total

    def test_naive_total_count_loses_half_of_missing_light(self):
        self.assertAlmostEqual(self.average('naive',[1,0]),1.5)

    def test_support_partition_restores_missing_light(self):
        self.assertAlmostEqual(self.average('support',[1,0]),2)

    def test_weighted_partition_keeps_origin_numerator(self):
        self.assertAlmostEqual(self.average('weighted',[4,0]),2)

    def test_empty_source_still_participates_in_support_normalizer(self):
        outcomes=merge_outcomes([(0,2,1),(None,0,1)],[1,1],[[1,1],[1,0]],'support')
        self.assertEqual(outcomes,[(0,1,1,0)])

    def test_chosen_light_rechecked_at_all_source_surfaces(self):
        outcomes=merge_outcomes([(1,2,1),(0,2,1)],[1,1],[[1,1],[1,0]],'support')
        self.assertEqual(outcomes,[(1,4,0.5,0),(0,2,0.5,1)])

    def test_unequal_source_counts_enter_both_weight_and_normalizer(self):
        outcomes=merge_outcomes([(1,2,1),(0,2,3)],[1,1],[[1,1],[1,0]],'support')
        self.assertEqual(outcomes,[(1,8,0.25,0),(0,2,0.75,1)])


class MeasureConversion(unittest.TestCase):
    def test_old_area_weight_does_not_freeze_growing_light(self):
        from reference import area_to_parameter
        f,h,p,w=area_to_parameter(2,1,1,.5,2)
        self.assertEqual(w,1)
        self.assertEqual(6*w,6)  # Current area is 6; its contribution in parameter measure is 6.
    def test_static_light_estimate_is_invariant_to_measure(self):
        from reference import area_to_parameter
        f,h,p,w=area_to_parameter(2,3,4,.25,4)
        self.assertEqual((f,h,p,w),(6,8,.5,2))
        self.assertEqual(f*w,12)
    def test_candidate_weight_uses_same_jacobian_in_target_and_pdf(self):
        from reference import area_to_parameter
        f,h,p,w=area_to_parameter(6,1,2,1/12,12)
        self.assertEqual((h,p),(12,.5))
        self.assertEqual(h/p,24)
    def test_degenerate_emitter_cannot_convert_measure(self):
        from reference import area_to_parameter
        with self.assertRaises(ValueError): area_to_parameter(0,1,1,1,1)

if __name__=='__main__': unittest.main(verbosity=2)
