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

class TestSwapAtLocations(unittest.TestCase):
    def test_single_location_left_boundary(self):
        mother = MagicMock()
        mother.starts = array("L", [0])
        mother.stops = array("L", [10])
        mother.founder = array("L", [1])
        father = MagicMock()
        father.starts = array("L", [0])
        father.stops = array("L", [10])
        father.founder = array("L", [2])
        locations = [(0, 5)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 5]))
        self.assertEqual(new_mother.stops, array("L", [5, 10]))
        self.assertEqual(new_mother.founder, array("L", [2, 1]))
        self.assertEqual(new_father.starts, array("L", [0, 5]))
        self.assertEqual(new_father.stops, array("L", [5, 10]))
        self.assertEqual(new_father.founder, array("L", [1, 2]))
        
    def test_single_location_right_boundary(self):
        mother = MagicMock()
        mother.starts = array("L", [0])
        mother.stops = array("L", [10])
        mother.founder = array("L", [1])
        father = MagicMock()
        father.starts = array("L", [0])
        father.stops = array("L", [10])
        father.founder = array("L", [2])
        locations = [(5, 10)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 5]))
        self.assertEqual(new_mother.stops, array("L", [5, 10]))
        self.assertEqual(new_mother.founder, array("L", [1, 2]))
        self.assertEqual(new_father.starts, array("L", [0, 5]))
        self.assertEqual(new_father.stops, array("L", [5, 10]))
        self.assertEqual(new_father.founder, array("L", [2, 1]))

    def test_single_location_middle_boundary(self):
        mother = MagicMock()
        mother.starts = array("L", [0])
        mother.stops = array("L", [10])
        mother.founder = array("L", [1])
        father = MagicMock()
        father.starts = array("L", [0])
        father.stops = array("L", [10])
        father.founder = array("L", [2])
        locations = [(2, 8)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 2, 8]))
        self.assertEqual(new_mother.stops, array("L", [2, 8, 10]))
        self.assertEqual(new_mother.founder, array("L", [1, 2, 1]))
        self.assertEqual(new_father.starts, array("L", [0, 2, 8]))
        self.assertEqual(new_father.stops, array("L", [2, 8, 10]))
        self.assertEqual(new_father.founder, array("L", [2, 1, 2]))

    def test_multiple_locations_single_segment(self):
        mother = MagicMock()
        mother.starts = array("L", [0])
        mother.stops = array("L", [10])
        mother.founder = array("L", [1])
        father = MagicMock()
        father.starts = array("L", [0])
        father.stops = array("L", [10])
        father.founder = array("L", [2])
        locations = [(0, 4), (6, 10)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 4, 6]))
        self.assertEqual(new_mother.stops, array("L", [4, 6, 10]))
        self.assertEqual(new_mother.founder, array("L", [2, 1, 2]))
        self.assertEqual(new_father.starts, array("L", [0, 4, 6]))
        self.assertEqual(new_father.stops, array("L", [4, 6, 10]))
        self.assertEqual(new_father.founder, array("L", [1, 2, 1]))

    def test_single_location_two_segments_first_segment(self):
        # TODO: CHANGE THIS
        mother = MagicMock()
        mother.starts = array("L", [0])
        mother.stops = array("L", [10])
        mother.founder = array("L", [1])
        father = MagicMock()
        father.starts = array("L", [0])
        father.stops = array("L", [10])
        father.founder = array("L", [2])
        locations = [(2, 8)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 2, 8]))
        self.assertEqual(new_mother.stops, array("L", [2, 8, 10]))
        self.assertEqual(new_mother.founder, array("L", [1, 2, 1]))
        self.assertEqual(new_father.starts, array("L", [0, 2, 8]))
        self.assertEqual(new_father.stops, array("L", [2, 8, 10]))
        self.assertEqual(new_father.founder, array("L", [2, 1, 2]))



    
if __name__ == '__main__':
    unittest.main()
