#!/usr/bin/env python3

import unittest

from common_segments import common_homolog_segments

class TestCommonHomologSegments(unittest.TestCase):
    def test_single_same_segment(self):
        a = [(0, 10, 0)]
        shared = common_homolog_segments(a, a)
        self.assertEqual(shared, [(0, 10)])

    def test_multiple_same_segment(self):
        a = [(0, 10, 0)]
        b = [(0, 5, 0), (5, 10, 0)]
        shared = common_homolog_segments(a, b)
        self.assertEqual(shared, [(0, 10)])
        
if __name__ == '__main__':
    unittest.main()
