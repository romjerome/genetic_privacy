from itertools import combinations
from random import sample
from time import perf_counter

import numpy as np

from population import PopulationUnpickler
from classify_relationship import shared_segment_length_genomes

print("Loading population")
with open("population_1000_array.pickle", "rb") as pickle_file:
    population = PopulationUnpickler(pickle_file).load()

print("Comparing pairs.")
nodes = population.generations[-1].members
# nodes = sample(nodes, 1000)
start = perf_counter()
lengths = [shared_segment_length_genomes(node_a.genome, node_b.genome, 0)
           for node_a, node_b in combinations(nodes, 2)]
stop = perf_counter()
print(stop - start)
# import pdb
# pdb.set_trace()
# shared = [len(np.flatnonzero(np.unpackbits(a.genome._founder_bits & b.genome._founder_bits)))
#           for a, b in combinations(nodes, 2)]

# print(np.average(shared))
# print(np.std(shared))
# print(max(lengths))
