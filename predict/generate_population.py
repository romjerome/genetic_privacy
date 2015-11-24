#!/usr/bin/env python3

from argparse import ArgumentParser
from random import choice
from pickle import dump, HIGHEST_PROTOCOL
from sys import setrecursionlimit, getrecursionlimit

from population import HierarchicalIslandPopulation
from population_genomes import generate_genomes
from node import Node
from recomb_genome import recombinators_from_directory, RecombGenomeGenerator
from island_model import tree_from_file
from sex import Sex

parser = ArgumentParser(description = "Generate a population and its associated genomes.")
parser.add_argument("tree_file",
                    help = "Describes hierarchical island model.")
parser.add_argument("recombination_dir",
                    help = "Directory containing Hapmap and decode data.")
parser.add_argument("--generation_size", type = int, default = 10000)
parser.add_argument("--num_generations", type = int, default = 10)
parser.add_argument("--output_file")

args = parser.parse_args()
if args.num_generations < 1:
    parser.error("num_generations must be >= 1")


founders = [Node() for _ in range(args.generation_size)]

tree = tree_from_file(args.tree_file)
leaves = tree.leaves
for person in founders:
    tree.add_individual(choice(leaves), person)
population = HierarchicalIslandPopulation(tree)

for _ in range(args.num_generations - 1):
    population.new_generation()

recombinators = recombinators_from_directory(args.recombination_dir)
chrom_sizes = recombinators[Sex.Male]._num_bases
genome_generator = RecombGenomeGenerator(chrom_sizes)
generate_genomes(population, genome_generator, recombinators)

if args.output_file:
    with open(args.output_file, "wb") as pickle_file:
        # Trees cause deep recursion in the pickle module, so we need
        # to raise the recursion limit. This is the stack depth for
        # python functions, you may need to increase the native stack
        # depth using ulimit -s
        # https://docs.python.org/3.4/library/pickle.html#what-can-be-pickled-and-unpickled
        old_limit = getrecursionlimit()
        new_limit = old_limit * args.num_generations * 100
        print("Setting stack depth to: {}.".format(new_limit))
        setrecursionlimit(new_limit)
        dump(population, pickle_file, protocol = HIGHEST_PROTOCOL)
        setrecursionlimit(old_limit)
