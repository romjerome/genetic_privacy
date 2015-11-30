from itertools import combinations, chain
from random import sample
from collections import Counter

import numpy as np

def proportion_within_distance(population, distance, percent_labeled):
    members = population.generations[-1].members
    num_labeled = int(percent_labeled * len(members))
    assert num_labeled > 0
    labeled = sample(members, num_labeled)
    ancestors = list()
    to_search = [(node, distance) for node in labeled]
    while len(to_search) > 0:
        current_node, current_distance = to_search.pop()
        assert current_node.mother is not None
        assert current_node.father is not None
        if current_distance == 1:
            ancestors.append(current_node.mother)
            ancestors.append(current_node.father)
            continue
        to_search.append((current_node.mother, current_distance - 1))
        to_search.append((current_node.father, current_distance - 1))
    assert len(to_search) is 0
    descendant_set = set()
    to_search.extend(ancestors)
    while len(to_search) > 0:
        current_node = to_search.pop()
        if current_node in descendant_set:
            continue
        descendant_set.add(current_node)
        to_search.extend(current_node.children)
    return len(descendant_set.intersection(members)) / len(members)

def descendants_of(node):
    descendants = set()
    to_visit = list(node.children)
    while len(to_visit) > 0:
        ancestor = to_visit.pop()
        descendants.add(ancestor)
        to_visit.extend(ancestor.children)
    return descendants

def ancestors_of(node, distance):
    assert distance > 0
    to_visit = [(node, 0)]
    ancestors = set()
    while len(to_visit) > 0:
        current_node, current_distance = to_visit.pop()
        assert current_node is not None
        if current_distance == distance:
            ancestors.add(current_node)
            continue
        to_visit.append((current_node.mother, current_distance + 1))
        to_visit.append((current_node.father, current_distance + 1))
    

def cdf_num_labeled_within_distance(population, distance, percent_labeled):
    members = population.generations[-1].members
    num_labeled = int(percent_labeled * len(members))
    assert num_labeled > 0
    labeled = sample(members, num_labeled)
    ancestors = set(chain.from_iterable(ancestors_of(labeled_node, distance)
                                        for labeled_node in labeled))
    
    counter = Counter(chain.from_itrable(descendants_of(ancestor)
                                         for ancestor in ancestors))
    for member in members:
        if member not in counter:
            counter[member] = 0

    # key is the number of people labeled within distance, and value
    # is the number of people who have this many labeled people within
    # that distance.
    # eg if value_counts[3] is 5, then 5 people have relations of the
    # given distance with with 3 labeled individuals.
    value_counts = Counter(counter.values())
    assert len(members) == sum(value_counts.values())
    total_count = len(members)
    x = sorted(value_counts.keys())
    y = np.cumsum([value_counts[key] for key in x]) / total_count
    return (np.array(x), y)

def length_shared(population):
    pass

def most_recent_common_ancestor(population):
    last_generation = population.generations[-1]
    for pair in combinations(last_generation.members):
        pass
