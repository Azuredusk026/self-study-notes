"""Deterministic explanatory timing model; no GPU execution."""
import unittest

def finish(g,c,s,l,early=True,handoff=0):
    c_start=g if early else g+s
    return max(g+s,c_start+handoff+c)+handoff+l

class ScheduleTests(unittest.TestCase):
    def test_serial(self): self.assertEqual(sum([2,3,4,2]),11)
    def test_overlap(self): self.assertEqual(finish(2,3,4,2),8)
    def test_late_signal(self): self.assertEqual(finish(2,3,4,2,False,.5),12)
    def test_contention(self): self.assertEqual(finish(2,5,6,2),10)
    def test_bandwidth(self): self.assertEqual(1920*1080*8*2,33177600)

if __name__=='__main__': unittest.main()
