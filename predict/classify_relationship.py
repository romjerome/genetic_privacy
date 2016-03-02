from collections import namedtuple, defaultdict
from itertools import chain
from random import choice, randrange

from scipy.stats import gamma

from common_segments import common_segment_lengths
from util import descendants_of

# loc is mean, scale is standard deviation
NormalDistribution = namedtuple("NormalDistribution", ["loc", "scale"])

# Distributions we want to have a lot of data samples for
DESIRED_DISTRIBUTIONS = [(2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (1,), (2,)]
# The minimum number of data points we must have on a relationship to
# generate a distribution for that relationship.
MINIMUM_DATAPOINTS = 50

class LengthClassifier:
    """
    Classifies based total length of shared segments
    """
    def __init__(self, population, minimum_segment_length = 0):
        self._minimum_segment_length = minimum_segment_length
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
            # if i % 1000 == 0 and _stop_sampling(length_counts):
            #     # Don't check the stop condition every time for efficiency
            #     break
            if i == 100000:
                break
            
        # Generate our conditional probabilities
        for vector, lengths in length_counts.items():
            if len(lengths) < MINIMUM_DATAPOINTS or max(lengths) == 0:
                continue
            fit = gamma.fit(lengths)
            distribution = gamma(*fit)
            self._distributions[vector] = distribution

    def has_relationship(self, relationship):
        """
        Returns true if this LengthClassifier can return probabilities
        for this type of relationship.
        """
        return relationship in self._distributions
            
    def get_probability_genomes(self, relationship, genome_a, genome_b):
        length = shared_segment_length_genomes(genome_a, genome_b,
                                               self._minimum_segment_length)
        if relationship in self._distributions:
            return self._distributions[relationship].pdf(length)
        else:
            # TODO: return something more meaningful here
            return None

    def classify(self, node_a, node_b):
        length = _shared_segment_length(node_a, node_b,
                                        self._minimum_segment_length)
        best_relationship = -1
        best_likelihood = -1
        for relationship, distribution in self._distributions.items():
            likelihood = distribution.pdf(length)
            if likelihood > best_likelihood:
                best_likelihood = likelihood
                best_relationship = relationship
        return best_relationship

def _stop_sampling(length_counts):
    # TODO: improve this condition.
    datapoints = (length_counts[key] for key in DESIRED_DISTRIBUTIONS)
    return min(len(datapoint_list) for datapoint_list in datapoints) > 100

def _pair_picker(population):
    """
    Returns random pairs of individuals from the last
    generations_to_use generations of population.
    TODO: Improve this sampling algorithm to get better data.
    """
    generations = population.generations
    with_genomes = population._generations_with_genomes
    compared_generations = [generation.members for generation in generations]
    # If we just chose random pairs from the population, few would be
    # closely related, thus we want to chose pair that we know share
    # recent common ancestors.
    while True:
        # We can't have someone in the latest generation as an ancestor
        ancestor_generation = randrange(population.num_generations - 1)
        ancestor = choice(compared_generations[ancestor_generation])
        descendants = descendants_of(ancestor)
        pairs = set()
        lower_generation_bound = max(ancestor_generation + 1,
                                     population.num_generations - with_genomes)
        for _ in range(10): # reuse an ancestor a few times.
            node_a_generation = randrange(lower_generation_bound,
                                          population.num_generations)
            node_b_generation = randrange(lower_generation_bound,
                                          population.num_generations)
            possible_node_a = list(descendants.intersection(compared_generations[node_a_generation]))
            possible_node_b = list(descendants.intersection(compared_generations[node_b_generation]))
            if len(possible_node_a) == 0 or len(possible_node_b) == 0:
                continue
            node_a = choice(possible_node_a)
            node_b = choice(possible_node_b)
            node_set = frozenset((node_a, node_b)) # ensure no repeats
            if node_set not in pairs and node_a is not node_b:
                yield (node_a, node_b)
                pairs.add(node_set)
    
def shared_segment_length_genomes(genome_a, genome_b, minimum_length):
    by_autosome = common_segment_lengths(genome_a, genome_b)
    seg_lengths = filter(lambda x: x >= minimum_length,
                         chain.from_iterable(by_autosome.values()))
    return sum(seg_lengths)
    
def _shared_segment_length(node_a, node_b, minimum_length):
    return shared_segment_length_genomes(node_a.genome, node_b.genome,
                                          minimum_length)

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
