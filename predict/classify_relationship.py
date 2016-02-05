from collection import namedtuple
from itertools import chain

from scipy.stats import norm

from util import get_sample_of_cousins
from common_segments import common_segment_lengths

# loc is mean, scale is standard deviation
NormalDistribution = namedtuple("NormalDistribution", ["loc", "scale"])

class LengthClassifier:
    """
    Classifies based total length of shared segments
    """
    def __init__(self, population, maximum_distance = 7, minimum_length = 0):
        distributions = dict()
        for distance in range(1, maxiumum_distance + 1):
            lengths = []
            pairs = get_sample_of_cousins(population, distance,
                                          percent_descendants = 0.5)
            for p_1, p_2 in pairs:
                by_autosome = common_segment_lengths(p_1.genome, p_2.genome)
                seg_lengths = filter(lambda x: x >= minimum_length,
                                     chain.from_iterable(by_autosome.values()))
                lengths.append(sum(seg_lengths))
            fit = norm.fit(lengths)
            distribution = NormalDistribution(fit[0], fit[1])
            distributions[distance] = distribution
        self._distributions = distributions

    def classify(self, length):
        best_distance = -1
        best_likelihood = -1
        for distance, distribution in distributions.items():
            likelihood = norm.pdf(length, distribution.loc, distribution.scale)
            if likelihood > best_likelihood:
                best_likelihood = likelihood
                best_distance = distance
        return best_distance

def _ancestors_of(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    ancestors = set()
    for node in nodes:
        ancestors.add(node.mother)
        ancestors.add(node.father)
    return ancestors
    
def common_ancestor_vector(population, node_a, node_b):
    """
    Return a vector with where each entry is the length of a path from
    person_a to person_b through a common ancestor.
    """
    node_to_generation = population.node_to_generation
    if node_to_generation[node_a] > node_to_generation[node_b]:
        temp = node_a
        node_a = node_b
        node_b = node_a
    node_a_generation = node_to_generation[node_a]
    node_b_generation = node_to_generation[node_b]
    ancestors_a = [node_a]
    ancestors_b = [node_b]
    while node_a_generation < node_b_generation:
        ancestors_b = _ancestors_of(ancestors_b)
        if node_a in ancestors_b:
            # One is a descandant of the other, therefore one of the
            # nodes is the only common ancestor which doesn't have a
            # path through a more recent common ancestor.
            return [node_b_generation - node_a_generation]
        node_b_generation -= 1
    distances_vector = []
    assert node_a_generation == node_b_generation
    for current_generation in range(node_a_generation - 1, -1, -1):
        a_ancestors = _ancestors_of(a_ancestors)
        b_ancestors = _ancestors_of(b_ancestors)
        common_ancestors = a_ancestors.intersection(b_ancestors)
        distance_to_a = node_to_generation[node_a] - current_generation
        distance_to_b = node_to_generation[node_b] - current_generation
        #TODO Pick up here
        distances_vector.extend([distance_to_a + distance_to_b] * len(commoon_ancestors))
            
            
