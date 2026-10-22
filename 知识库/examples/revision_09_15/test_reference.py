"""CPU checks: coordinate conventions and finite-domain RIS estimates."""
import itertools
import math
import unittest
import reference as r


class Mechanisms(unittest.TestCase):
    def test_transaction_precondition_failure_reverts_completed_steps(self):
        state = []
        def reject():
            raise ValueError('stale plan')
        result = r.execute_plan([
            (lambda: None, lambda: state.append('first'), lambda: state.pop()),
            (reject, lambda: state.append('second'), lambda: state.pop()),
        ])
        self.assertEqual(state, [])
        self.assertEqual(result, (False, 'stale plan', []))

    def test_transaction_compensation_continues_after_failure(self):
        events = []
        def bad_revert():
            events.append('revert-second')
            raise OSError('locked file')
        def fail_apply():
            raise ValueError('write failed')
        result = r.execute_plan([
            (lambda: None, lambda: events.append('first'), lambda: events.append('revert-first')),
            (lambda: None, lambda: events.append('second'), bad_revert),
            (lambda: None, fail_apply, lambda: events.append('unexpected')),
        ])
        self.assertEqual(events, ['first', 'second', 'revert-second', 'revert-first'])
        self.assertEqual(result, (False, 'write failed', ['locked file']))

    def test_transaction_success_does_not_compensate(self):
        state = []
        self.assertEqual(r.execute_plan([
            (lambda: None, lambda: state.append(1), lambda: state.pop()),
            (lambda: None, lambda: state.append(2), lambda: state.pop()),
        ]), (True, None, []))
        self.assertEqual(state, [1, 2])

    def test_retarget_reference_is_identity(self):
        self.assertEqual(r.retarget(((1, 0), (0, 1)), ((0, -1), (1, 0))), ((1, 0), (0, 1)))

    def test_retarget_rotated_basis_preserves_action(self):
        # A 90-degree rotation about source x becomes one about target y.
        delta = ((1, 0, 0), (0, 0, -1), (0, 1, 0))
        basis = ((0, -1, 0), (1, 0, 0), (0, 0, 1))
        self.assertEqual(r.retarget(delta, basis), ((0, 0, 1), (0, 1, 0), (-1, 0, 0)))

    def test_iris_front_view_has_no_offset(self):
        self.assertEqual(r.iris_uv((.5, .5), (0, 0, 1), .1), (.5, .5))

    def test_iris_oblique_view_moves_opposite_view(self):
        self.assertEqual(r.iris_uv((.5, .5), (1, 0, 1), .1), (.4, .5))

    def test_iris_grazing_view_is_rejected(self):
        self.assertIsNone(r.iris_uv((.5, .5), (1, 0, 0), .1))

    def test_face_front_side_back_threshold(self):
        self.assertEqual([r.face_threshold(x, z) for x, z in [(0, 1), (1, 0), (0, -1)]], [0, .5, 1])

    def test_face_vertical_direction_fallback(self):
        self.assertEqual(r.face_threshold(0, 0), .25)

    def test_ris_exhaustive_mean(self):
        # Independent two-sample proposals on a finite, uniform domain.
        target, contribution = (1., 3.), (2., 5.)
        mean = 0.
        for candidates in itertools.product(range(2), repeat=2):
            weights = [target[y] / .5 for y in candidates]
            for y, w in zip(candidates, weights):
                p = w / sum(weights)
                mean += .25 * p * r.ris_estimate(contribution[y], target[y], sum(weights), 2)
        self.assertAlmostEqual(mean, sum(contribution))

    def test_ris_zero_stream_returns_zero(self):
        self.assertEqual(r.ris_estimate(0, 0, 0, 2), 0)

    def test_merged_reservoir_reweights_target(self):
        # Two reservoirs, each representing one deterministic proposal point.
        self.assertEqual(r.merge_weight(4, .5, 3), 6)

    def test_merged_changed_target_mean(self):
        target, f = (4., 1.), (2., 5.)
        # Each source sampled its domain point with pdf 1/2, so W=2.
        weights = [r.merge_weight(t, 2., 1) for t in target]
        mean = sum(w / sum(weights) * r.ris_estimate(v, t, sum(weights), 2)
                   for w, v, t in zip(weights, f, target))
        self.assertAlmostEqual(mean, 7.)


if __name__ == '__main__':
    unittest.main(verbosity=2)
