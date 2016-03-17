#!/usr/bin/env python3

import unittest
from unittest.mock import MagicMock

import pyximport; pyximport.install()
from common_ancestor_vector import common_ancestor_vector

class MockNode:
    def __init__(self, mother = None, father = None):
        self.mother = mother
        self.father = father

class TestCommonAncestorVector(unittest.TestCase):
    def test_parent_child(self):
        mother = MockNode()
        child = MockNode(mother)
        generation = MagicMock()
        generation.node_to_generation = {mother: 0, child: 1}
        vector = common_ancestor_vector(generation, mother, child)
        self.assertEqual(vector, (1,))

    def test_parent_child_flip(self):
        mother = MockNode()
        child = MockNode(mother)
        generation = MagicMock()
        generation.node_to_generation = {mother: 0, child: 1}
        vector = common_ancestor_vector(generation, child, mother)
        self.assertEqual(vector, (1,))

    def test_grandparent_child(self):
        grandmother = MockNode()
        mother = MockNode(grandmother)
        child = MockNode(mother)
        generation = MagicMock()
        generation.node_to_generation = {grandmother: 0, mother: 1, child: 2}
        vector = common_ancestor_vector(generation, grandmother, child)
        self.assertEqual(vector, (2,))
        
    def test_half_sibling(self):
        mother = MockNode()
        node_a = MockNode(mother)
        node_b = MockNode(mother)
        generation = MagicMock()
        generation.node_to_generation = {mother: 0, node_a: 1, node_b: 1}
        vector = common_ancestor_vector(generation, node_a, node_b)
        self.assertEqual(vector, (2,))
        
    def test_full_sibling(self):
        mother = MockNode()
        father = MockNode()
        node_a = MockNode(mother, father)
        node_b = MockNode(mother, father)
        generation = MagicMock()
        generation.node_to_generation = {mother: 0, father: 0,
                                         node_a: 1, node_b: 1}
        vector = common_ancestor_vector(generation, node_a, node_b)
        self.assertEqual(vector, (2, 2))

    def test_full_sibling_more_ancestors(self):
        grandmother_a = MockNode()
        grandfather_a = MockNode()
        grandmother_b = MockNode()
        grandfather_b = MockNode()
        mother = MockNode(grandmother_a, grandfather_a)
        father = MockNode(grandmother_b, grandfather_b)
        node_a = MockNode(mother, father)
        node_b = MockNode(mother, father)
        generation = MagicMock()
        generation.node_to_generation = {grandmother_a: 0, grandfather_a: 0,
                                         grandmother_b: 0, grandfather_b: 0,
                                         mother: 1, father: 1,
                                         node_a: 2, node_b: 2}
        vector = common_ancestor_vector(generation, node_a, node_b)
        self.assertEqual(vector, (2, 2))

    def test_cousins(self):
        grandmother = MockNode()
        grandfather = MockNode()
        sibling_a = MockNode(grandmother, grandfather)
        sibling_b = MockNode(grandmother, grandfather)
        cousin_a = MockNode(sibling_a)
        cousin_b = MockNode(sibling_b)
        generation = MagicMock()
        generation.node_to_generation = {grandmother: 0, grandfather: 0,
                                         sibling_a: 1, sibling_b: 1,
                                         cousin_a: 2, cousin_b: 2}
        
        vector = common_ancestor_vector(generation, cousin_a, cousin_b)
        self.assertEqual(vector, (4, 4))

    def test_double_first_cousins(self):
        grandmother_a = MockNode()
        grandfather_a = MockNode()
        grandmother_b = MockNode()
        grandfather_b = MockNode()
        sibling_a1 = MockNode(grandmother_a, grandfather_a)
        sibling_a2 = MockNode(grandmother_a, grandfather_a)
        sibling_b1 = MockNode(grandmother_b, grandfather_b)
        sibling_b2 = MockNode(grandmother_b, grandfather_b)
        cousin_a = MockNode(sibling_a1, sibling_b1)
        cousin_b = MockNode(sibling_a2, sibling_b2)
        generation = MagicMock()
        generation.node_to_generation = {grandmother_a: 0, grandfather_a: 0,
                                         grandmother_b: 0, grandfather_b: 0,
                                         sibling_a1: 1, sibling_a2: 1,
                                         sibling_b1: 1, sibling_b2: 1,
                                         cousin_a: 2, cousin_b: 2}
        vector = common_ancestor_vector(generation, cousin_a, cousin_b)
        self.assertEqual(vector, (4, 4, 4, 4))

    def test_sibling_cousins(self):
        grandmother = MockNode()
        grandfather = MockNode()
        sibling_a = MockNode(grandmother, grandfather)
        sibling_b = MockNode(grandmother, grandfather)
        shared_father = MockNode()
        sibling_cousin_a = MockNode(sibling_a, shared_father)
        sibling_cousin_b = MockNode(sibling_b, shared_father)
        generation = MagicMock()
        generation.node_to_generation = {grandmother: 0, grandfather: 0,
                                         sibling_a: 1, sibling_b: 1,
                                         shared_father: 1, sibling_cousin_a: 2,
                                         sibling_cousin_b: 2}
        
        vector = common_ancestor_vector(generation, sibling_cousin_a,
                                        sibling_cousin_b)
        self.assertEqual(vector, (2, 4, 4))


if __name__ == '__main__':
    unittest.main()
