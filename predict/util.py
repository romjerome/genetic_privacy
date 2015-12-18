from collections import deque
from random import sample

def get_sample_of_cousins(population, distance, percent_ancestors = 0.1):
    """
    return a sample of individuals whos most recent common ancestor is
    exactly generations back.
    """
    assert distance > 0
    common_ancestors = population.generations[-(distance + 1)]
    ancestors_sample = sample(common_ancestors,
                              int(len(common_ancestors) * percent_ancestors))
    descendants = set()

def descendants_of(node):
    descendants = set()
    to_visit = list(node.children)
    while len(to_visit) > 0:
        ancestor = to_visit.pop()
        descendants.add(ancestor)
        to_visit.extend(ancestor.children)
    return descendants

def get_n_degree_relations(ancestor, distance):
    """
    Returns pairs of individuals separated by distance generations,
    starting from ancestor.
    """
    # Find the descendents of the children, remove the pairwise
    # intersection, and return pairs from different sets.
    ancestor_children = ancestor.children
    descendant_sets = []
    for child in ancestor_children:
        descendent_sets.append(descendants_of(child))
    


