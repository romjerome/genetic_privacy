#!/usr/bin/env python3
from genome import GenomeGenerator
import cProfile
import pdb


generator = GenomeGenerator()
genome = generator.generate_genome()
# cProfile.run("generator.generate_genome()")
pdb.set_trace()
