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

def get_n_degree_relations(ancestor, generation_members):
    """
    Returns pairs of individuals descendent from ancestor in the given
    generation who have ancestor as their most recent ancestor.
    """
    # Find the descendents of the children, remove the pairwise
    # intersection, and return pairs from different sets.
    ancestor_children = ancestor.children
    assert len(ancestor_children) > 1
    descendant_sets = [descendants_of(child).intersection(generation_members)
                       for child in ancestor_children]    
    
