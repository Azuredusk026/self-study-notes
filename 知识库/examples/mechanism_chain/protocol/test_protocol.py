import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from reference import Store, Gesture


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'state.db'
        self.store = Store(self.path)

    def test_only_prepared_snapshot_can_change_owner(self):
        self.assertFalse(self.store.transfer('A', 7, 'B', 'missing'))
        self.store.prepare('m')
        self.assertTrue(self.store.transfer('A', 7, 'B', 'm'))
        self.assertFalse(self.store.transfer('A', 7, 'C', 'm'))
        self.assertEqual(self.store.state(), ('B', 8, 3, 100))

    def test_crash_before_commit_does_not_consume_or_apply(self):
        self.store.close()
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('reference.py')),
                              str(self.path), 'before'], check=False)
        self.assertEqual(run.returncode, 19)
        self.store = Store(self.path)
        self.assertEqual(self.store.state(), ('A', 7, 3, 100))
        self.assertEqual(self.store.consume('A', 7, 101), 'applied')
        self.assertEqual(self.store.state()[2:], (2, 101))

    def test_crash_after_commit_replay_does_not_repeat_effect(self):
        self.store.close()
        run = subprocess.run([sys.executable, str(Path(__file__).with_name('reference.py')),
                              str(self.path), 'after'], check=False)
        self.assertEqual(run.returncode, 19)
        self.store = Store(self.path)
        self.assertEqual(self.store.consume('A', 7, 101), 'duplicate')
        self.assertEqual(self.store.state()[2:], (2, 101))

    def test_fencing_and_gap_reject_without_effect(self):
        self.store.prepare('m')
        self.store.transfer('A', 7, 'B', 'm')
        self.assertEqual(self.store.consume('A', 7, 101), 'fenced')
        self.assertEqual(self.store.consume('B', 8, 102), 'gap')
        self.assertEqual(self.store.state()[2:], (3, 100))

    def test_new_session_does_not_treat_sequence_one_as_old_duplicate(self):
        self.assertTrue(self.store.switch_session('session-1', 'session-2', drained=True))
        self.assertEqual(self.store.consume('A', 7, 101, session='session-1'), 'session')
        self.assertEqual(self.store.consume('A', 7, 1, session='session-2'), 'applied')
        self.assertEqual(self.store.state()[2:], (2, 1))

    def test_pending_queue_prevents_session_reset(self):
        self.assertFalse(self.store.switch_session('session-1', 'session-2', drained=False))
        self.assertEqual(self.store.consume('A', 7, 101), 'applied')

    def test_generation_cas_preserves_external_edit_after_publish(self):
        self.store.plan_output('job', b'generated')
        self.assertEqual(self.store.publish('job'), 'published')
        self.store.external_edit(b'human')
        self.assertEqual(self.store.recover_output('job'), 'conflict')
        self.assertEqual(self.store.output(), (2, b'human'))

    def test_recovery_completes_publish_without_republishing(self):
        self.store.plan_output('job', b'generated')
        self.store.publish('job')
        self.assertEqual(self.store.recover_output('job'), 'succeeded')
        self.assertEqual(self.store.output(), (1, b'generated'))

    def test_output_aba_still_conflicts(self):
        self.store.plan_output('job', b'generated')
        self.store.external_edit(b'other')
        self.store.external_edit(b'old')
        self.assertEqual(self.store.publish('job'), 'conflict')
        self.assertEqual(self.store.output(), (2, b'old'))

    def test_drag_keeps_first_old_and_last_new(self):
        values = {'id': 1}
        gesture = Gesture(values)
        gesture.begin('id')
        for value in [2, 3, 9]:
            gesture.update(value)
        command = gesture.commit()
        self.assertEqual(command, ('id', 1, 9))
        gesture.undo(command)
        self.assertEqual(values['id'], 1)
        gesture.redo(command)
        self.assertEqual(values['id'], 9)

    def test_cancel_does_not_add_undo_record(self):
        values = {'id': 4}
        gesture = Gesture(values)
        gesture.begin('id')
        gesture.update(8)
        self.assertEqual(values['id'], 8)
        gesture.cancel()
        self.assertEqual(values['id'], 4)
        self.assertIsNone(gesture.commit())

    def tearDown(self):
        self.store.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
