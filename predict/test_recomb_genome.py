#!/usr/bin/env python3

from bisect import bisect_left
from unittest.mock import MagicMock
from array import array
import unittest

import recomb_genome

def break_sequence_wrapper(sequence, location):
    return recomb_genome._break_sequence(sequence, location,
                                         bisect_left(sequence, (location,)))

class TestNewSequence(unittest.TestCase):
    def test_single_element_middle(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0])
        diploid.stops = array("L", [10])
        diploid.founder = array("L", [1])
        ret_diploid = recomb_genome._new_sequence(diploid, [5])
        self.assertEqual(ret_diploid.starts, [0, 5])
        self.assertEqual(ret_diploid.stops, [5, 10])
        self.assertEqual(ret_diploid.founder, [1, 1])


    def test_single_element_start(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0])
        diploid.stops = array("L", [10])
        diploid.founder = array("L", [1])
        ret_diploid = recomb_genome._new_sequence(diploid, [0])
        self.assertEqual(ret_diploid.starts, [0])
        self.assertEqual(ret_diploid.stops, [10])
        self.assertEqual(ret_diploid.founder, [1])

    def test_end_boundary_two_element(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0, 10])
        diploid.stops = array("L", [10, 20])
        diploid.founder = array("L", [1, 2])
        ret_diploid = recomb_genome._new_sequence(diploid, [10])
        self.assertEqual(ret_diploid.starts, [0, 10])
        self.assertEqual(ret_diploid.stops, [10, 20])
        self.assertEqual(ret_diploid.founder, [1, 2])

    def test_start_boundary_two_element(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0, 10])
        diploid.stops = array("L", [10, 20])
        diploid.founder = array("L", [1, 2])
        ret_diploid = recomb_genome._new_sequence(diploid, [0])
        self.assertEqual(ret_diploid.starts, [0, 10])
        self.assertEqual(ret_diploid.stops, [10, 20])
        self.assertEqual(ret_diploid.founder, [1, 2])

    def test_middle_boundary_two_element(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0, 10])
        diploid.stops = array("L", [10, 20])
        diploid.founder = array("L", [1, 2])
        ret_diploid = recomb_genome._new_sequence(diploid, [5])
        self.assertEqual(ret_diploid.starts, [0, 5, 10])
        self.assertEqual(ret_diploid.stops, [5, 10, 20])
        self.assertEqual(ret_diploid.founder, [1, 1, 2])

    def test_middle_boundary_two_element_multiple_breaks(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0, 10])
        diploid.stops = array("L", [10, 20])
        diploid.founder = array("L", [1, 2])
        ret_diploid = recomb_genome._new_sequence(diploid, [5, 15])
        self.assertEqual(ret_diploid.starts, [0, 5, 10, 15])
        self.assertEqual(ret_diploid.stops, [5, 10, 15, 20])
        self.assertEqual(ret_diploid.founder, [1, 1, 2, 2])

    def test_single_element_end(self):
        diploid = MagicMock()
        diploid.starts = array("L", [0])
        diploid.stops = array("L", [10])
        diploid.founder = array("L", [1])
        ret_diploid = recomb_genome._new_sequence(diploid, [10])
        self.assertEqual(ret_diploid.starts, [0] )
        self.assertEqual(ret_diploid.stops, [10] )
        self.assertEqual(ret_diploid.founder, [1] )

    
if __name__ == '__main__':
    unittest.main()
