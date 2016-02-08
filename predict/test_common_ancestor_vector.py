#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock

from classify_relationship import common_ancestor_vector

class MockNode:
    def __init__(self, mother = None, father = None):
        self.mother = mother
        self.father = father

class TestCommonAncestorVector(unittest.TestCase):
    def test_share_single_mother(self):
        mother = MockNode()
        node_a = MockNode(mother)
        node_b = MockNode(mother)
        generation = MagicMock()
        generation.node_to_generation = {mother: 0, node_a: 1, node_b: 2}
        vector = common_ancestor_vector(generation, node_a, node_b)
        self.assertEqual(vector, [2])

if __name__ == '__main__':
    unittest.main()
