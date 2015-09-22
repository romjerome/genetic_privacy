from random import choice, sample, uniform
from itertools import zip_longest

import numpy as np

SNP_OCCURENCE = 1/100
SNP_COUNT = [50, 100, 150]
# 1 centimorgan is on average 1 million bases in humans and 1
# centimorgan is defined as the distance for a recombination
# probability to be 1%
RECOMBINATION_RATE = 1/1000000 * 1/100
# TODO: Use something other than constant recomination rate throughout autosome


# From https://en.wikipedia.org/wiki/Human_genome
# TODO: fill in
HUMAN_AUTOSOME_LENGTHS = [249250621, 243199373, 198022430]

#TODO: NEED TO GENERATE LOCATIONS FOR SNPs.

class GenomeGenerator():
    def __init__(self, autosome_count = 1, snp_count = SNP_COUNT):
        # For each autosome, contains a lists of allele pairs for each SNP
        self._alleles = []
        # For each autosome, contains a list of the loci for SNPs
        self._gene_locations = []
        # For each autosome, contains a list of frequencies of each
        # allele in self._alleles in the general population. The given
        # number represents the frequency of the first allele pair in
        # self._alleles.
        self._allele_frequency = []
        for i in range(autosome_count):
            autosome_size = choice(snp_count) * 1000
            frequency = np.random.random(autosome_size)
            # Ensure that the minor allele frequency is at least SNP_OCCURENCE%
            # by adjusting the range of the random generator.
            frequency = (1 - 2 * SNP_OCCURENCE) * frequency + SNP_OCCURENCE
            self._allele_frequency.append(frequency)
            nucleotides = [0, 1, 2, 3]
            self._alleles.append([sample(nucleotides, 2) for i in range(autosome_size)])
            locations = self._generate_snp_locations(HUMAN_AUTOSOME_LENGTHS[i],
                                                     autosome_size)
            self._gene_locations.append(locations)
                        
    def _generate_snp_locations(self, chromosome_size, snp_count):
        """
        Generate SNP locations along the genome.
        """
        return np.sort(np.random.choice(chromosome_size, snp_count,
                                        replace = False))

            

    def generate_genome(self):
        autosomes = []
        for frequencies, alleles in zip(self._allele_frequency,
                                         self._alleles):
            homolog_1 = [_pick_allele(allele_pair, frequency)
                        for frequency, allele_pair in zip(frequencies, alleles)]
            homolog_2 = [_pick_allele(allele_pair, frequency)
                        for frequency, allele_pair in zip(frequencies, alleles)]
            autosomes.append((np.array(homolog_1, dtype = np.uint8),
                              np.array(homolog_2, dtype = np.uint8)))
        return Genome(autosomes, self._gene_locations)

def _pick_allele(alleles, prob):
    """
    Return the first element in alleles with probability prob,
    thus the second element with 1 - prob.
    """
    if uniform(0, 1) < prob:
        return alleles[0]
    return alleles[1]

def recombination(autosome_pair, autosome_num, gene_locations):
    # Model the number of recombination locations as n independent coin flips.
    num_recombination = np.random.binomial(HUMAN_AUTOSOME_LENGTHS[autosome_num],
                                           RECOMBINATION_RATE)
    locations = np.random.choice(HUMAN_AUTOSOME_LENGTHS[autosome_num],
                                 num_recombination, replace = False)
    recombination_indices = np.searchsorted(gene_locations, locations,
                                            side = "right")
    for start, stop in zip_longest(recombination_indices[::2],
                                   recombination_indices[1::2]):
        if stop is None:
            # This recombination event goes to the end of the strand
            stop = len(gene_locations) - 1
        temp = np.copy(autosome_pair[0][start:stop])
        autosome_pair[0][start:stop] = autosome_pair[1][start:stop]
        autosome_pair[1][start:stop] = temp

            
            
    return autosome_pair

class Genome():
    def __init__(self, autosomes, gene_locations):
        self._autosomes = autosomes
        self._locations = gene_locations

    def mate(self, other):
        offspring_autosomes = []
        for i, autosome_pair in enumerate(self._autosomes):
            this_parent_autosome = choice(recombination(autosome_pair, i,
                                                        self._locations[i]))
            other_parent_autosome = choice(recombination(other._autosomes[i], i,
                                                         other._locations[i]))
            offspring_autosomes.append((this_parent_autosome,
                                        other_parent_autosome))
        return Genome(offspring_autosomes, self._locations)
    
