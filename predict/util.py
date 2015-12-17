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

def get_n_degree_relations(ancestor, distance):
    """
    Returns pairs of individuals separated by distance generations,
    starting from ancestor.
    """
    # Do a BFS from the ancestor down to the children, saving the path
    # to the children. Then pairwise compare the paths of children, if
    # they have an overlapping parent along the path before the
    # original ancestor, they are not a path separated by the desired
    # distance.
    # Is there a way to do this without comparing all possible pairs?
    to_explore = deque(ancestor.children)
    while len(to_explore) > 0:
        pass


