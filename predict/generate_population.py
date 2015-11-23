#!/usr/bin/env python3

from argparse import ArgumentParser
from random import choice

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
