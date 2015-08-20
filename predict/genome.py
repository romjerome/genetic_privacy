from random import choice, sample
import numpy as np

class GenomeGenerator():
    def __init__(self, autosome_count = 22, densities = [50, 100, 150]):
        self._allele_frequency = []
        self._alleles = []
        for i in range(autosome_count):
            autosome_size = choice(densities)
            frequency = np.random.random(autosome_size)
            # Ensure that the minor allele frequency is at least 1%
            # by adjusting the range of the random generator.
            frequency = (99/100 - 1 / 100) * frequency + 1/100
            self._allele_frequency.append(frequency)
            nucleotides = [0, 1, 2, 3]
            self._alleles.append([sample(nucleotides, 2) for i in range(autosome_size)])
            alleles_split = zip(*alleles)

            

    def generate_genome(self):
        pass

class Genome():
    def __init__(self, autosomes):
        self._autosomes = autosomes
    
