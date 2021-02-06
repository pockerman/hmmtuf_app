import unittest
from compute_engine.src.tufdel import gcpercent

class TestUtils(unittest.TestCase):

    def test_gc_percent_1(self):

        array = "tactgaggtg"
        out = gcpercent(cseq=array, chunk_size=100)
        self.assertEqual(out, "50_NA_NA")

    def test_gc_percent_2(self):

        array = "tactgaggtg"
        out = gcpercent(cseq=array, chunk_size=2)
        self.assertEqual(out, "50_0_100")

    def test_gc_percent_3(self):

        array = "tactgaggtg"*11
        out = gcpercent(cseq=array, chunk_size=100)
        self.assertEqual(out, "50_50_50")





if __name__ == '__main__':
    unittest.main()


