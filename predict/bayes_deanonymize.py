from classify_relationship import LengthClassifier, common_ancestor_vector,\
    shared_segment_length_genomes
from functools import reduce
from operator import mul

MINIMUM_LABELED_NODES = 10

class BayesDeanonymize:
    def __init__(self, population, labeled_nodes):
        self._population = population
        self._labeled_nodes = list(labeled_nodes)
        self._length_classifier = LengthClassifier(population, 1000)

    def _compare_genome_node(self, node, genome):
        probabilities = []
        for labeled_node in self._labeled_nodes:
            ancestor_vector = common_ancestor_vector(node, labeled_node)
            prob = self._length_classifier.get_probability(ancestor_vector,
                                                           node.genome,
                                                           genome)
            probabilities.append(probability)
        return list(filter(lambda x: x is not None, probabilities))

        
    def identify(self, genome):
        node_probabilities = dict() # Probability that a node is a match
        for member in self._population.members:
            if member.genome is None:
                continue
            proabilities = self._compare_genome_node(member, genome)]
            if len(probabilites) < MINIMUM_LABELED_NODES:
                # We don't want to base our estimation on datapoints
                # from too few labeled nodes.
                continue
            node_probabilities[node] = reduce(mul, proabilities, 1)
        return max(node_probabilities.iteritems(), key = lambda x: x[1])[0]
