import unittest
try:
    from reference import valid, latent_query, mix_normal, keyframe
except ImportError:
    valid=latent_query=mix_normal=keyframe=None
class VideoTests(unittest.TestCase):
    def test_rejections(self):
        self.assertIsNotNone(valid,'历史判定实现缺失')
        self.assertEqual(valid((10,10),(100,100),7,7,2,2,.9,.1,False),'accept')
        for args,reason in [(((-1,10),(100,100),7,7,2,2,.9,.1,False),'bounds'),(((10,10),(100,100),7,8,2,2,.9,.1,False),'identity'),(((10,10),(100,100),7,7,2,1,.9,.1,False),'depth'),(((10,10),(100,100),7,7,2,2,.1,.1,False),'confidence'),(((10,10),(100,100),7,7,2,2,.9,.1,True),'cut')]:
            self.assertEqual(valid(*args),reason)
    def test_mapping_normal_and_anchor(self):
        self.assertIsNotNone(latent_query,'尺度换算实现缺失')
        self.assertEqual(latent_query((20,10),(-8,0),8), (19,10))
        self.assertEqual(mix_normal((1,0,0),(-1,0,0),.5),(1,0,0))
        self.assertEqual(keyframe(10,20,.75,.25,False),12.5)
        self.assertEqual(keyframe(10,20,.75,.25,True),10)
    def test_no_valid_anchor_even_when_conflicting(self):
        with self.assertRaises(ValueError): keyframe(10,20,0,0,True)
if __name__=='__main__': unittest.main()
