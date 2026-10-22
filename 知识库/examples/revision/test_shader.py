import unittest
from shader_models import blocked_scan, ReadbackModel, blocked_minmax

class ShaderModels(unittest.TestCase):
    def test_minmax_partial_signed_groups(self):
        for count in (1,63,64,65,130,257):
            for sign in (-1,1):
                values=[sign*(1+(i*13)%37) for i in range(count)]
                self.assertEqual(blocked_minmax(values),(min(values),max(values)))

    def test_minmax_empty_and_single(self):
        self.assertIsNone(blocked_minmax([]))
        self.assertEqual(blocked_minmax([7]),(7,7))

    def test_scan_across_partial_groups(self):
        for count in (0,1,63,64,65,130,257):
            values=[(i*7)%5 for i in range(count)]
            expected=[sum(values[:i]) for i in range(count)]
            self.assertEqual(blocked_scan(values), (expected,sum(values)))
    def test_scan_stable_compaction(self):
        flags=[0,1,1,0,1,0,1]
        offsets,total=blocked_scan(flags,4)
        out=[None]*total
        for i,flag in enumerate(flags):
            if flag: out[offsets[i]]=i
        self.assertEqual(out,[1,2,4,6])
    def test_full_ring_and_out_of_order_completion(self):
        ring=ReadbackModel(2)
        self.assertTrue(ring.submit(8)); self.assertTrue(ring.submit(9))
        self.assertFalse(ring.submit(10))
        ring.complete(9,'new'); ring.complete(8,'old')
        self.assertEqual(ring.latest,(9,'new'))
        self.assertTrue(ring.submit(10))
        ring.complete(10,'broken',error=True)
        self.assertEqual(ring.latest,(9,'new'))
    def test_cancel_discards_publication_but_retires_request(self):
        ring=ReadbackModel(1)
        ring.submit(1);ring.invalidate()
        self.assertFalse(ring.submit(2))
        ring.complete(1,'stale')
        self.assertIsNone(ring.latest)
        self.assertTrue(ring.submit(2))
        ring.complete(2,'current')
        self.assertEqual(ring.latest,(2,'current'))

if __name__=='__main__': unittest.main()
