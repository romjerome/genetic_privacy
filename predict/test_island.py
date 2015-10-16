#!/usr/bin/env python3

from island_model import tree_from_file

tree = tree_from_file("test_tree")

num_leaves = len(tree.leaves)
assert num_leaves is 3, "Expected 3 leaves, got {}".format(num_leaves)
