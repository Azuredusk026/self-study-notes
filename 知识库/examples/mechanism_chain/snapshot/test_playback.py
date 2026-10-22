import unittest
from playback import Playback


class PlaybackCases(unittest.TestCase):
    def test_extrapolation_cap_stops_timestamp_as_well_as_pose(self):
        p=Playback(0.95)
        self.assertEqual(p.step(0.2,0.2,1.2,[0.85,0.9]),1.0)
        self.assertEqual(p.mode,'frozen')
        self.assertEqual(p.step(0.4,0.2,1.4,[0.85,0.9]),1.0)

    def test_one_packet_does_not_restart_unbuffered_playback(self):
        p=Playback(0.95)
        p.step(0.2,0.2,1.2,[0.85,0.9])
        self.assertEqual(p.step(0.3,0.1,1.3,[0.9,1.05]),1.0)
        self.assertEqual(p.mode,'frozen')

    def test_refilled_buffer_resumes_from_frozen_timestamp(self):
        p=Playback(0.95)
        p.step(0.2,0.2,1.2,[0.85,0.9])
        self.assertEqual(p.step(0.4,0.2,1.4,[1.0,1.2]),1.0)
        self.assertEqual(p.mode,'playing')
        self.assertGreater(p.step(0.5,0.1,1.5,[1.0,1.1,1.3]),1.0)

    def test_timeout_enters_explicit_resync_then_anchors_inside_buffer(self):
        p=Playback(0.95)
        p.step(0.2,0.2,1.2,[0.85,0.9])
        self.assertEqual(p.step(1.0,0.8,2.0,[0.85,0.9]),1.0)
        self.assertEqual(p.mode,'waiting')
        self.assertEqual(p.step(1.1,0.1,2.1,[1.8,1.85,1.9]),1.85)
        self.assertEqual(p.mode,'playing')
        self.assertEqual(p.generation,1)

    def test_old_right_endpoint_cannot_rewind_resync(self):
        p=Playback(0.95)
        p.step(0.2,0.2,1.2,[0.85,0.9])
        p.step(1.0,0.8,2.0,[0.85,0.9])
        self.assertEqual(p.step(1.1,0.1,2.1,[0.95,0.99]),1.0)
        self.assertEqual(p.mode,'waiting')

    def test_large_backlog_uses_explicit_anchor_instead_of_endless_speedup(self):
        p=Playback(1.0)
        self.assertEqual(p.step(0.1,0.1,2.0,[1.0,1.5,2.0]),1.0)
        self.assertEqual(p.mode,'waiting')
        self.assertEqual(p.step(0.2,0.1,2.1,[1.0,1.5,2.0]),1.5)


if __name__=='__main__': unittest.main(verbosity=2)
