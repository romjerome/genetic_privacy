from collections import defaultdict
from itertools import chain
from random import choice, randrange

from scipy.stats import gamma
import pyximport; pyximport.install()

from common_segments import common_segment_lengths
from common_ancestor_vector import common_ancestor_vector
from util import descendants_of

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
        self._length_cache = dict()
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
            if i == 200000:
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
            
    def get_probability(self, relationship, genome_a, genome_b):
        pair = (genome_a, genome_b)
        if pair in self._length_cache:
            length = self._length_cache[pair]
        else:
            length = shared_segment_length_genomes(genome_a, genome_b,
                                                   self._minimum_segment_length)
            self._length_cache[pair] = length
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

