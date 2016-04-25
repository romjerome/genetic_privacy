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
        mother = MagicMock()
        mother.starts = array("L", [0, 10])
        mother.stops = array("L", [10, 20])
        mother.founder = array("L", [1, 2])
        father = MagicMock()
        father.starts = array("L", [0, 10])
        father.stops = array("L", [10, 20])
        father.founder = array("L", [3, 4])
        locations = [(0, 10)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 10]))
        self.assertEqual(new_mother.stops, array("L", [10, 20]))
        self.assertEqual(new_mother.founder, array("L", [3, 2]))
        self.assertEqual(new_father.starts, array("L", [0, 10]))
        self.assertEqual(new_father.stops, array("L", [10, 20]))
        self.assertEqual(new_father.founder, array("L", [1, 4]))

    def test_single_location_two_segments_last_segment(self):
        mother = MagicMock()
        mother.starts = array("L", [0, 10])
        mother.stops = array("L", [10, 20])
        mother.founder = array("L", [1, 2])
        father = MagicMock()
        father.starts = array("L", [0, 10])
        father.stops = array("L", [10, 20])
        father.founder = array("L", [3, 4])
        locations = [(10, 20)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 10]))
        self.assertEqual(new_mother.stops, array("L", [10, 20]))
        self.assertEqual(new_mother.founder, array("L", [1, 4]))
        self.assertEqual(new_father.starts, array("L", [0, 10]))
        self.assertEqual(new_father.stops, array("L", [10, 20]))
        self.assertEqual(new_father.founder, array("L", [3, 2]))


    def test_single_location_overlapping_two_segments(self):
        mother = MagicMock()
        mother.starts = array("L", [0, 10])
        mother.stops = array("L", [10, 20])
        mother.founder = array("L", [1, 2])
        father = MagicMock()
        father.starts = array("L", [0, 10])
        father.stops = array("L", [10, 20])
        father.founder = array("L", [3, 4])
        locations = [(5, 15)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 5, 10, 15]))
        self.assertEqual(new_mother.stops, array("L", [5, 10, 15, 20]))
        self.assertEqual(new_mother.founder, array("L", [1, 3, 4, 2]))
        self.assertEqual(new_father.starts, array("L", [0, 5, 10, 15]))
        self.assertEqual(new_father.stops, array("L", [5, 10, 15, 20]))
        self.assertEqual(new_father.founder, array("L", [3, 1, 2, 4]))

    def test_single_location_overlapping_three_segments(self):
        mother = MagicMock()
        mother.starts = array("L", [0, 10, 20])
        mother.stops = array("L", [10, 20, 30])
        mother.founder = array("L", [1, 2, 3])
        father = MagicMock()
        father.starts = array("L", [0, 10, 20])
        father.stops = array("L", [10, 20, 30])
        father.founder = array("L", [4, 5, 6])
        locations = [(5, 25)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 5, 10, 20, 25]))
        self.assertEqual(new_mother.stops, array("L", [5, 10, 20, 25, 30]))
        self.assertEqual(new_mother.founder, array("L", [1, 4, 5, 6, 3]))
        self.assertEqual(new_father.starts, array("L", [0, 5, 10, 20, 25]))
        self.assertEqual(new_father.stops, array("L", [5, 10, 20, 25, 30]))
        self.assertEqual(new_father.founder, array("L", [4, 1, 2, 3, 6]))

    def test_two_locations_at_boundary_two_segments (self):
        mother = MagicMock()
        mother.starts = array("L", [0, 10])
        mother.stops = array("L", [10, 20])
        mother.founder = array("L", [1, 2])
        father = MagicMock()
        father.starts = array("L", [0, 10])
        father.stops = array("L", [10, 20])
        father.founder = array("L", [3, 4])
        locations = [(0, 5), (15, 20)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 5, 10, 15]))
        self.assertEqual(new_mother.stops, array("L", [5, 10, 15, 20]))
        self.assertEqual(new_mother.founder, array("L", [3, 1, 2, 4]))
        self.assertEqual(new_father.starts, array("L", [0, 5, 10, 15]))
        self.assertEqual(new_father.stops, array("L", [5, 10, 15, 20]))
        self.assertEqual(new_father.founder, array("L", [1, 3, 4, 2]))

    def test_two_locations_at_boundary_two_segments(self):
        mother = MagicMock()
        mother.starts = array("L", [0, 10])
        mother.stops = array("L", [10, 20])
        mother.founder = array("L", [1, 2])
        father = MagicMock()
        father.starts = array("L", [0, 10])
        father.stops = array("L", [10, 20])
        father.founder = array("L", [3, 4])
        locations = [(2, 5), (15, 18)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 2, 5, 10, 15, 18]))
        self.assertEqual(new_mother.stops, array("L", [2, 5, 10, 15, 18, 20]))
        self.assertEqual(new_mother.founder, array("L", [1, 3, 1, 2, 4, 2]))
        self.assertEqual(new_father.starts, array("L", [0, 2, 5, 10, 15, 18]))
        self.assertEqual(new_father.stops, array("L", [2, 5, 10, 15, 18, 20]))
        self.assertEqual(new_father.founder, array("L", [3, 1, 3, 4, 2, 4]))

    
    def test_single_location_two_segments_uneven(self):
        mother = MagicMock()
        mother.starts = array("L", [0, 5])
        mother.stops = array("L", [5, 20])
        mother.founder = array("L", [1, 2])
        father = MagicMock()
        father.starts = array("L", [0, 10])
        father.stops = array("L", [10, 20])
        father.founder = array("L", [3, 4])
        locations = [(2, 11)]
        new_mother, new_father = recomb_genome._swap_at_locations(mother,
                                                                  father,
                                                                  locations)
        self.assertEqual(new_mother.starts, array("L", [0, 2, 10, 11]))
        self.assertEqual(new_mother.stops, array("L", [2, 10, 11, 20]))
        self.assertEqual(new_mother.founder, array("L", [1, 3, 4, 2]))
        self.assertEqual(new_father.starts, array("L", [0, 2, 5, 11]))
        self.assertEqual(new_father.stops, array("L", [2, 5, 11, 20]))
        self.assertEqual(new_father.founder, array("L", [3, 1, 2, 4]))



    
if __name__ == '__main__':
    unittest.main()
