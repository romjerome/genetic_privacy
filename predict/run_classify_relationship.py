#!/usr/bin/env python3

from random import sample
from itertools import chain
from pickle import dump

from population import PopulationUnpickler
from sex import Sex
from classify_relationship import generate_classifier
from recomb_genome import recombinators_from_directory, RecombGenomeGenerator

OUTPUT_DIR = "/media/paul/Storage/scratch/lengths"
print("Loading population")
with open("population_10000.pickle", "rb") as pickle_file:
    population = PopulationUnpickler(pickle_file).load()

print("Loading recombination data.")
recombinators = recombinators_from_directory("../data/recombination_rates/")
chrom_sizes = recombinators[Sex.Male]._num_bases
genome_generator = RecombGenomeGenerator(chrom_sizes)

potentially_labeled = list(chain.from_iterable([generation.members
                                                for generation
                                                in population.generations[-3:]]))
labeled_nodes = sample(potentially_labeled, 500)
print("Populating length classifier.")
classifier = generate_classifier(population, labeled_nodes, genome_generator,
                                 recombinators, OUTPUT_DIR, iterations = 3)

print("Pickling classifier")
with open("classifier.pickle", "wb") as pickle_file:
    dump(classifier, pickle_file)

# import pdb
# pdb.set_trace()
