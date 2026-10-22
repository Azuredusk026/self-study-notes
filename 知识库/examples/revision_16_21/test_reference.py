"""机制边界测试；不代表真实网络、引擎或持久化故障测试。"""
import pathlib
import tempfile
import unittest
import reference as r


class Network(unittest.TestCase):
    def test_clock_excludes_server_processing(self):
        offset, delay = r.clock_sample(0, 5.1, 5.3, .4)
        self.assertAlmostEqual(offset, 5.0)
        self.assertAlmostEqual(delay, .2)

    def test_clock_asymmetric_bias(self):
        offset, delay = r.clock_sample(0, 5.15, 5.15, .2)
        self.assertAlmostEqual(offset, 5.05)
        self.assertAlmostEqual(delay, .2)

    def test_wrapped_sequence(self):
        self.assertTrue(r.newer(0, 65535))
        self.assertFalse(r.newer(65535, 0))
        self.assertFalse(r.newer(8, 8))

    def test_reconcile_replays_collision(self):
        # x=8, ack=65535；0号到墙停在10，1号再退1，应为9。
        self.assertEqual(r.reconcile(8, 65535, [(65535, 9), (0, 5), (1, -1)], 10), 9)

    def test_history_rejects_extrapolation(self):
        self.assertEqual(r.history([(10, 2), (12, 6)], 11), 4)
        with self.assertRaises(ValueError):
            r.history([(10, 2), (12, 6)], 9)

    def test_ray_hits_nearest_forward_surface(self):
        self.assertAlmostEqual(r.ray_sphere((0,0,0), (1,0,0), (5,0,0), 1), 4)
        self.assertIsNone(r.ray_sphere((0,0,0), (1,0,0), (-5,0,0), 1))

    def test_rpc_retry_and_payload_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            db = pathlib.Path(d) / 'ledger.db'
            self.assertEqual(r.credit(db, 'a', 'txn', 10), 10)
            self.assertEqual(r.credit(db, 'a', 'txn', 10), 10)
            with self.assertRaises(ValueError):
                r.credit(db, 'a', 'txn', 11)
            self.assertEqual(r.credit(db, 'a', 'next', 3), 13)

    def test_rpc_failure_rolls_back_balance(self):
        with tempfile.TemporaryDirectory() as d:
            db = pathlib.Path(d) / 'ledger.db'
            with self.assertRaises(RuntimeError):
                r.credit(db, 'a', 'txn', 10, fail_before_record=True)
            self.assertEqual(r.credit(db, 'a', 'txn', 10), 10)

    def test_rollback_corrects_state_and_rebuilds_events(self):
        self.assertEqual(r.rollback([1,1,1], 1, -1), (1, [(0,1), (1,0), (2,1)]))


class Physics(unittest.TestCase):
    def test_xpbd_pinned_particle(self):
        x0,x1,lam = r.xpbd(0,2,0,1,1,0,.1,0)
        self.assertEqual((x0,x1), (0,1))
        self.assertEqual(lam, -1)

    def test_xpbd_compliance_and_accumulation(self):
        x0,x1,lam = r.xpbd(0,2,0,1,1,.01,.1,0)
        self.assertAlmostEqual(x1, 1.5)
        again = r.xpbd(x0,x1,0,1,1,.01,.1,lam)
        self.assertAlmostEqual(again[1], x1)

    def test_xpbd_coincident_rejected(self):
        with self.assertRaises(ValueError):
            r.xpbd(1,1,1,1,1,0,.1,0)

    def test_fracture_support_disconnect(self):
        self.assertEqual(r.unsupported(5, [(0,1),(1,2),(3,4)], {0}), [{3,4}])

    def test_tire_shared_force_budget(self):
        fx,fy = r.tire_limit(4000,3000,1,2500)
        self.assertEqual((fx,fy), (2000,1500))
        self.assertEqual(r.tire_limit(1,2,1,0), (0,0))

    def test_slide_retains_tangent(self):
        self.assertEqual(r.slide((2,-3,0),(0,1,0)), (2,0,0))
        self.assertEqual(r.slide((2,3,0),(0,1,0)), (2,3,0))


class Storage(unittest.TestCase):
    def test_atomic_publish_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)/'asset.bin'
            r.publish(p,b'old')
            r.publish(p,b'new')
            self.assertTrue(p.exists())
            self.assertEqual(p.read_bytes(), b'new')
            self.assertEqual(list(pathlib.Path(d).iterdir()), [p])

    def test_atomic_publish_failure_preserves_destination(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)/'asset.bin'
            p.write_bytes(b'old')
            with self.assertRaises(RuntimeError):
                r.publish(p,b'new',fail_before_replace=True)
            self.assertEqual(p.read_bytes(), b'old')
            self.assertEqual(list(pathlib.Path(d).iterdir()), [p])


if __name__ == '__main__':
    unittest.main(verbosity=2)
