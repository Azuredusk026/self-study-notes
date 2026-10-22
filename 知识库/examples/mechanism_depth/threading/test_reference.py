import unittest
from reference import QueueModel, predicate, publication

class ProtocolTests(unittest.TestCase):
    def test_two_consumers_one_item(self):
        q=QueueModel();q.push(17)
        self.assertEqual(q.pop(),('item',17))
        self.assertEqual(q.pop(),('wait',None))
    def test_close_drains_then_exits(self):
        q=QueueModel();q.push(2);q.push(3);q.close()
        self.assertFalse(q.push(4))
        self.assertEqual([q.pop(),q.pop(),q.pop()],[('item',2),('item',3),('exit',None)])
    def test_all_predicate_states(self):
        self.assertEqual([predicate(c,n) for c,n in [(False,0),(False,1),(True,0),(True,1)]],[False,True,True,True])
    def test_notification_has_no_item(self):
        q=QueueModel()
        for _ in range(10):self.assertEqual(q.pop(),('wait',None))
        q.close();self.assertEqual(q.pop(),('exit',None))
    def test_publication_reads_corresponding_value(self):
        self.assertFalse(publication('release','acquire',False))
        self.assertTrue(publication('release','acquire',True))
        self.assertFalse(publication('relaxed','relaxed',True))

if __name__=='__main__':unittest.main()
