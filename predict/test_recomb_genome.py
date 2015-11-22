#!/usr/bin/env python3

from bisect import bisect_left
import unittest

import recomb_genome

def break_sequence_wrapper(sequence, location):
    return recomb_genome._break_sequence(sequence, location,
                                         bisect_left(sequence, (location,)))

class TestBreakSequence(unittest.TestCase):

    def test_single_element_middle(self):
        sequence = [(0, 10, 1)]
        break_sequence_wrapper(sequence, 5)
        self.assertEqual(sequence, [(0, 5, 1), (5, 10, 1)])
                         
    def test_single_element_end_range(self):
        sequence = [(0, 10, 1)]
        break_sequence_wrapper(sequence, 10)
        self.assertEqual(sequence, [(0, 10, 1)])

    def test_single_element_start_range(self):
        sequence = [(0, 10, 1)]
        break_sequence_wrapper(sequence, 0)
        self.assertEqual(sequence, [(0, 10, 1)])

    def test_two_element_start_range_last_element(self):
        sequence = [(0, 10, 1), (10, 20, 2)]
        break_sequence_wrapper(sequence, 10)
        self.assertEqual(sequence, [(0, 10, 1), (10, 20, 2)])

    def test_two_element_middle_first_index(self):
        sequence = [(0, 10, 1), (10, 20, 2)]
        break_sequence_wrapper(sequence, 5)
        self.assertEqual(sequence, [(0, 5, 1), (5, 10, 1), (10, 20, 2)])
        
    def test_two_element_last_location(self):
        sequence = [(0, 10, 1), (10, 20, 2)]
        break_sequence_wrapper(sequence, 20)
        self.assertEqual(sequence, [(0, 10, 1), (10, 20, 2)])

    def test_two_element_first_location(self):
        sequence = [(0, 10, 1), (10, 20, 2)]
        break_sequence_wrapper(sequence, 0)
        self.assertEqual(sequence, [(0, 10, 1), (10, 20, 2)])

class TestSwap(unittest.TestCase):
    def test_single_location_left_boundary(self):
        mother = [(0, 10, 1)]
        father = [(0, 10, 2)]
        locations = [(0, 5)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 5, 2), (5, 10, 1)])
        self.assertEqual(father, [(0, 5, 1), (5, 10, 2)])

    def test_single_location_right_boundary(self):
        mother = [(0, 10, 1)]
        father = [(0, 10, 2)]
        locations = [(5, 10)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 5, 1), (5, 10, 2)])
        self.assertEqual(father, [(0, 5, 2), (5, 10, 1)])

    def test_single_location_middle_boundary(self):
        mother = [(0, 10, 1)]
        father = [(0, 10, 2)]
        locations = [(2, 8)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 2, 1), (2, 8, 2), (8, 10, 1)])
        self.assertEqual(father, [(0, 2, 2), (2, 8, 1), (8, 10, 2)])
        
    def test_multiple_locations_single_segment(self):
        mother = [(0, 10, 1)]
        father = [(0, 10, 2)]
        locations = [(0, 4), (6, 10)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 4, 2), (4, 6, 1), (6, 10, 2)])
        self.assertEqual(father, [(0, 4, 1), (4, 6, 2), (6, 10, 1)])

    def test_single_location_two_segments_first_segment(self):
        mother = [(0, 10, 1), (10, 20, 2)]
        father = [(0, 10, 3), (10, 20, 4)]
        locations = [(0, 10)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 10, 3), (10, 20, 2)])
        self.assertEqual(father, [(0, 10, 1), (10, 20, 4)])

    def test_single_location_two_segments_last_segment(self):
        mother = [(0, 10, 1), (10, 20, 2)]
        father = [(0, 10, 3), (10, 20, 4)]
        locations = [(10, 20)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 10, 1), (10, 20, 4)])
        self.assertEqual(father, [(0, 10, 3), (10, 20, 2)])

    def test_single_location_overlapping_two_segments(self):
        mother = [(0, 10, 1), (10, 20, 2)]
        father = [(0, 10, 3), (10, 20, 4)]
        locations = [(5, 15)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 5, 1), (5, 10, 3),
                                  (10, 15, 4), (15, 20, 2)])
        self.assertEqual(father, [(0, 5, 3), (5, 10, 1),
                                  (10, 15, 2), (15, 20, 4)])
        
    def test_single_location_overlapping_three_segments(self):
        mother = [(0, 10, 1), (10, 20, 2), (20, 30, 3)]
        father = [(0, 10, 4), (10, 20, 5), (20, 30, 6)]
        locations = [(5, 25)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 5, 1), (5, 10, 4),
                                  (10, 20, 5), (20, 25, 6), (25, 30, 3)])
        self.assertEqual(father, [(0, 5, 4), (5, 10, 1),
                                  (10, 20, 2), (20, 25, 3), (25, 30, 6)])

    def test_two_locations_at_boundary_two_segments(self):
        mother = [(0, 10, 1), (10, 20, 2)]
        father = [(0, 10, 3), (10, 20, 4)]
        locations = [(0, 5), (15, 20)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 5, 3), (5, 10, 1), (10, 15, 2),
                                  (15, 20, 4)])
        self.assertEqual(father, [(0, 5, 1), (5, 10, 3), (10, 15, 4),
                                  (15, 20, 2)])

    def test_two_locations_at_boundary_two_segments(self):
        mother = [(0, 10, 1), (10, 20, 2)]
        father = [(0, 10, 3), (10, 20, 4)]
        locations = [(2, 5), (15, 18)]
        recomb_genome._swap_at_locations(mother, father, locations)
        self.assertEqual(mother, [(0, 2, 1), (2, 5, 3), (5, 10, 1), (10, 15, 2),
                                  (15, 18, 4), (18, 20, 2)])
        self.assertEqual(father, [(0, 2, 3), (2, 5, 1), (5, 10, 3), (10, 15, 4),
                                  (15, 18, 2), (18, 20, 4)])
    
if __name__ == '__main__':
    unittest.main()
