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

