#!/usr/bin/env python3
from genome import GenomeGenerator
import cProfile
import pdb


generator = GenomeGenerator(autosome_count = 1)
genome_1 = generator.generate_genome()
genome_2 = generator.generate_genome()
genome_3 = genome_1.mate(genome_2)
# cProfile.run("generator.generate_genome()")
pdb.set_trace()
