from itertools import combinations, product, chain
from random import sample


def get_sample_of_cousins(population, distance, percent_ancestors = 0.1):
    """
    return a sample of individuals whos most recent common ancestor is
    exactly generations back.
    """
    assert distance > 0
    common_ancestors = population.generations[-(distance + 1)].members
    last_generation = set(population.generations[-1].members)
    ancestors_sample = sample(common_ancestors,
                              int(len(common_ancestors) * percent_ancestors))
    pairs = []
    for ancestor in ancestors_sample:
        temp_pairs = descendants_with_common_ancestor(ancestor, last_generation)
        temp_pairs = list(temp_pairs)
        pairs.extend(sample(temp_pairs, int(len(temp_pairs) * 0.1)))
    return pairs

def descendants_of(node):
    descendants = set()
    to_visit = list(node.children)
    while len(to_visit) > 0:
        ancestor = to_visit.pop()
        descendants.add(ancestor)
        to_visit.extend(ancestor.children)
    return descendants

def descendants_with_common_ancestor(ancestor, generation_members):
    """
    Returns pairs of individuals descendent from ancestor in the given
    generation who have ancestor as their most recent ancestor.
    """
    # Find the descendents of the children, remove the pairwise
    # intersection, and return pairs from different sets.
    ancestor_children = ancestor.children
    if len(ancestor_children) < 2:
        return []
    if generation_members.is_superset(ancestor_children):
        # Depth is only 1 generation, so return all combinations of children.
        return combinations(ancestor_children, 2)
    descendant_sets = [descendants_of(child).intersection(generation_members)
                       for child in ancestor_children]    
    pair_iterables = []
    for descendants_a , descendants_b in combinations(descendant_sets, 2):
        intersection = descendants_a.intersection(descendants_b)
        if len(intersection) > 0:
            # Remove individuals who have a more recent common ancestor
            descendants_a = descendants_a - intersection
            descendants_b = descendants_b - intersection
        pair_iterables.append(product(descendants_a, descendants_b))
    return chain.from_iterable(pair_iterables)

