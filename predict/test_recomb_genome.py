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
    
if __name__ == '__main__':
    unittest.main()
