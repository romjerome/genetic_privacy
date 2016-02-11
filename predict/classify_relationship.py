from collections import namedtuple, defaultdict
from itertools import chain
from random import choice, random, sample

from scipy.stats import norm

from common_segments import common_segment_lengths
from util import descendants_of

import pdb

# loc is mean, scale is standard deviation
NormalDistribution = namedtuple("NormalDistribution", ["loc", "scale"])

# Distributions we want to have a lot of data samples for
DESIRED_DISTRIBUTIONS = [(2, 2), (4, 4)]

class LengthClassifier:
    """
    Classifies based total length of shared segments
    """
    def __init__(self, population, minimum_segment_length = 0):
        self._distributions = dict()
        length_counts = defaultdict(list)
        i = 0
        for node_a, node_b in _pair_picker(population):
            relationship_vector = common_ancestor_vector(population, node_a,
                                                         node_b)
            shared_length = _shared_segment_length(node_a, node_b,
                                                   minimum_segment_length)
            length_counts[relationship_vector].append(shared_length)
            i += 1
            if i % 1000 == 0 and _stop_sampling(length_counts):
                # Don't check the stop condition every time for efficiency
                break
        for vector, lengths in length_counts.items():            
            fit = norm.fit(lengths)
            distribution = NormalDistribution(fit[0], fit[1])
            self._distributions[vector] = distribution

    def classify(self, length):
        best_distance = -1
        best_likelihood = -1
        for distance, distribution in self._distributions.items():
            likelihood = norm.pdf(length, distribution.loc, distribution.scale)
            if likelihood > best_likelihood:
                best_likelihood = likelihood
                best_distance = distance
        return best_distance

def _stop_sampling(length_counts):
    # TODO: improve this condition.
    (lengs_counts[key] for key in DESIRED_DISTRIBUTIONS)
    return (min(len(lengths) for lengths in ) > 100)

def _pair_picker(population, generations_to_use = 3):
    """
    Returns random pairs of individuals from the last
    generations_to_use generations of population.]
    TODO: Improve this sampling algorithm to get better data.
    """
    generations = population.generations
    compared_generations = [generation.members for generation
                            in generations[-generations_to_use:]]
    # If we just chose random pairs from the population, few would be
    # closely related, thus we want to chose pair that we know share
    # recent common ancestors.
    while True:
        strategy = random()
        if strategy < 0.3:
            descendants = list(descendants_of(choice(compared_generations[0])))
            if len(descendants) <= 1:
                continue
            node_a, node_b = sample(descendants, 2)
            yield(node_a, node_b)
        elif strategy < 0.6:
            descendants = list(descendants_of(choice(compared_generations[1])))
            if len(descendants) <= 1:
                continue
            node_a, node_b = sample(descendants, 2)
            yield(node_a, node_b)
        elif strategy < 0.9:
            yield(choice(compared_generations[2]),
                  choice(compared_generations[2]))
        else:
            yield (choice(choice(compared_generations)),
                   choice(choice(compared_generations)))
    

def _shared_segment_length(node_a, node_b, minimum_length):
    by_autosome = common_segment_lengths(node_a.genome, node_b.genome)
    seg_lengths = filter(lambda x: x >= minimum_length,
                         chain.from_iterable(by_autosome.values()))
    return sum(seg_lengths)
    

def _immediate_ancestors_of(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    ancestors = set()
    for node in nodes:
        if node is None:
            continue
        ancestors.add(node.mother)
        ancestors.add(node.father)
    ancestors.discard(None)
    return ancestors
    
def common_ancestor_vector(population, node_a, node_b):
    """
    Return a vector with where each entry is the length of a path from
    person_a to person_b through a common ancestor.
    """
    if node_a == node_b:
        return (0,)
    node_to_generation = population.node_to_generation
    if node_to_generation[node_a] > node_to_generation[node_b]:
        temp = node_a
        node_a = node_b
        node_b = temp
    node_a_generation = node_to_generation[node_a]
    node_b_generation = node_to_generation[node_b]
    current_generation = node_b_generation
    ancestors_a = [node_a]
    ancestors_b = [node_b]
    while node_a_generation < current_generation:
        ancestors_b = _immediate_ancestors_of(ancestors_b)
        if node_a in ancestors_b:
            # One is a descandant of the other, therefore one of the
            # nodes is the only common ancestor which doesn't have a
            # path through a more recent common ancestor.
            return (node_b_generation - node_a_generation,)
        current_generation -= 1
    distances_vector = []
    assert node_a_generation == current_generation
    for current_generation in range(node_a_generation - 1, -1, -1):
        ancestors_a = _immediate_ancestors_of(ancestors_a)
        ancestors_b = _immediate_ancestors_of(ancestors_b)
        common_ancestors = ancestors_a.intersection(ancestors_b)
        distance_to_a = node_a_generation - current_generation
        distance_to_b = node_b_generation - current_generation
        new_distance = [distance_to_a + distance_to_b] * len(common_ancestors)
        distances_vector.extend(new_distance)
        # Don't look past the ancestors we have already counted.
        # eg it is more relevant that siblings share parents rather
        # than grandparents.
        ancestors_a.difference_update(common_ancestors)
        ancestors_b.difference_update(common_ancestors)
    distances_vector.sort() 
    return tuple(distances_vector)
