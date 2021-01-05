import unittest
from compute_engine.src.utils import min_size_partition_range
from compute_engine.src.exceptions import Error


class TestUtils(unittest.TestCase):

    def test_min_size_partition_range_1(self):
        start = 0
        end = 0
        minsize = 1
        self.assertRaises(Error, min_size_partition_range, start, end, minsize)

    def test_min_size_partition_range_2(self):
        start = 0
        end = 1
        minsize = 1
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 1)
        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 1)

    def test_min_size_partition_range_3(self):
        start = 0
        end = 10
        minsize = 2
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 5)

        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 2)

        self.assertEqual(chuncks[1][0], 2)
        self.assertEqual(chuncks[1][1], 4)

        self.assertEqual(chuncks[2][0], 4)
        self.assertEqual(chuncks[2][1], 6)

        self.assertEqual(chuncks[3][0], 6)
        self.assertEqual(chuncks[3][1], 8)

        self.assertEqual(chuncks[4][0], 8)
        self.assertEqual(chuncks[4][1], 10)

    def test_min_size_partition_range_4(self):
        start = 0
        end = 10
        minsize = 1
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 10)

        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 1)

        self.assertEqual(chuncks[1][0], 1)
        self.assertEqual(chuncks[1][1], 2)

        self.assertEqual(chuncks[2][0], 2)
        self.assertEqual(chuncks[2][1], 3)

        self.assertEqual(chuncks[3][0], 3)
        self.assertEqual(chuncks[3][1], 4)

        self.assertEqual(chuncks[4][0], 4)
        self.assertEqual(chuncks[4][1], 5)

        self.assertEqual(chuncks[5][0], 5)
        self.assertEqual(chuncks[5][1], 6)

        self.assertEqual(chuncks[6][0], 6)
        self.assertEqual(chuncks[6][1], 7)

        self.assertEqual(chuncks[7][0], 7)
        self.assertEqual(chuncks[7][1], 8)

        self.assertEqual(chuncks[8][0], 8)
        self.assertEqual(chuncks[8][1], 9)

        self.assertEqual(chuncks[9][0], 9)
        self.assertEqual(chuncks[9][1], 10)

    def test_min_size_partition_range_4(self):
        start = 0
        end = 10
        minsize = 3
        chuncks = min_size_partition_range(start, end, minsize)
        self.assertEqual(len(chuncks), 3)

        self.assertEqual(chuncks[0][0], 0)
        self.assertEqual(chuncks[0][1], 3)

        self.assertEqual(chuncks[1][0], 3)
        self.assertEqual(chuncks[1][1], 6)

        self.assertEqual(chuncks[2][0], 6)
        self.assertEqual(chuncks[2][1], 10)


if __name__ == '__main__':
    unittest.main()