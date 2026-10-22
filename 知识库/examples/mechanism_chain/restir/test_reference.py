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


if __name__=='__main__': unittest.main(verbosity=2)
