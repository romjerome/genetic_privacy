from random import choice, sample, uniform
import numpy as np

SNP_OCCURENCE = 1/100
DEFAULT_DENSITIES = [50, 100, 150]

class GenomeGenerator():
    def __init__(self, autosome_count = 22, densities = DEFAULT_DENSITIES):
        # For each autosome, contains a lists of allele pairs for each SNP
        self._alleles = []
        # For each autosome, contains a list of frequencies of each
        # allele in self._alleles in the general population. The given
        # number represents the frequency of the first allele pair in
        # self._alleles.
        self._allele_frequency = []
        for i in range(autosome_count):
            autosome_size = choice(densities) * 1000
            frequency = np.random.random(autosome_size)
            # Ensure that the minor allele frequency is at least SNP_OCCURENCE%
            # by adjusting the range of the random generator.
            frequency = (1 - 2 * SNP_OCCURENCE) * frequency + SNP_OCCURENCE
            self._allele_frequency.append(frequency)
            nucleotides = [0, 1, 2, 3]
            self._alleles.append([sample(nucleotides, 2) for i in range(autosome_size)])

            

    def generate_genome(self):
        autosomes = []
        for frequencies, alleles in zip(self._allele_frequency,
                                         self._alleles):
            autosome = [_pick_allele(allele_pair, frequency)
                        for frequency, allele_pair in zip(frequencies, alleles)]
            autosomes.append(np.array(autosome, dtype = np.uint8))
        return Genome(autosomes)

def _pick_allele(alleles, prob):
    """
    Return the first element in alleles with probability prob,
    thus the second element with 1 - prob.
    """
    if uniform(0, 1) < prob:
        return alleles[0]
    return alleles[1]

class Genome():
    def __init__(self, autosomes):
        self._autosomes = autosomes

    def mate(self, other):
        pass
    
