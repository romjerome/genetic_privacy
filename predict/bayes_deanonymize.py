import pyximport; pyximport.install()

from classify_relationship import LengthClassifier
from common_ancestor_vector import common_ancestor_vector
from functools import reduce
from operator import mul

MINIMUM_LABELED_NODES = 5

class BayesDeanonymize:
    def __init__(self, population, labeled_nodes):
        self._population = population
        self._labeled_nodes = list(labeled_nodes)
        self._length_classifier = LengthClassifier(population, 1000)
        self._vector_intern = dict() # To intern the vector objects
        self._vector_cache = dict()

    def _compare_genome_node(self, node, genome):
        probabilities = []
        for labeled_node in self._labeled_nodes:
            pair = (node, labeled_node)
            if pair in self._vector_cache:
                ancestor_vector = self._vector_cache[pair]
            else:
                ancestor_vector = common_ancestor_vector(self._population,
                                                         node, labeled_node)
                if ancestor_vector in self._vector_intern:
                    ancestor_vector = self._vector_intern[ancestor_vector]
                else:
                    self._vector_intern[ancestor_vector] = ancestor_vector
                self._vector_cache[pair] = ancestor_vector
                    
            prob = self._length_classifier.get_probability(ancestor_vector,
                                                           node.genome,
                                                           genome)
            probabilities.append(prob)
        return list(filter(lambda x: x is not None, probabilities))

        
    def identify(self, genome):
        node_probabilities = dict() # Probability that a node is a match
        for member in self._population.members:
            if member.genome is None:
                continue
            probabilities = self._compare_genome_node(member, genome)
            if len(probabilities) < MINIMUM_LABELED_NODES:
                # We don't want to base our estimation on datapoints
                # from too few labeled nodes.
                continue
            node_probabilities[member] = reduce(mul, probabilities, 1)
        return max(node_probabilities.items(), key = lambda x: x[1])[0]
