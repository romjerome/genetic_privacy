#!/usr/bin/env python3
"""
This scripts divides up a population so that length distributions can be comptued in parallel.
"""

from argparse import ArgumentParser
from itertools import chain
from random import sample
from pickle import load, dump
from os.path import join, isdir
from os import makedirs

from population import population_from_directory

parser = ArgumentParser(description = "Split up work for parallization")

parser.add_argument("population_dirname")
parser.add_argument("partition_size", type = int)
parser.add_argument("--labeled_nodes_file", default = None)
parser.add_argument("--num_labeled", type = int, default = 0)
parser.add_argument("--output_dir", default = ".")

args = parser.parse_args()
if args.partition_size <= 0:
    parser.error("Partition size must be > 0")
if args.labeled_nodes_file is None and args.num_labeled <= 0:
    parser.error("If no labeled nodes file is provided, positive num_labeled must be specified.")

print("Loading population")
population = population_from_directory(args.population_dirname)

if not isdir(args.output_dir):
    makedirs(args.output_dir)

print("Generating labeled nodes")
if args.labeled_nodes_file is None:
    valid_generations = population.generations[-population._generations_with_genomes:]
    potentially_labeled = list(chain.from_iterable(generation.members
                                                   for generation in
                                                   valid_generations))
    labeled_nodes = sample(potentially_labeled, args.num_labeled)
    labeled_filename = join(args.output_dir, "all_labeled_nodes.pickle")
    with open(labeled_filename, "wb") as pickle_file:
        dump(set(node._id for node in labeled_nodes), pickle_file)
else:
    mapping = population.id_mapping
    with open(args.labeled_nodes_file, "rb") as pickle_file:
        labeled_nodes = [mapping[node_id] for node_id in
                            load(pickle_file)]

print("Creating partitions")
partitions = [labeled_nodes[i:i + args.partition_size]
              for i in range(0, len(labeled_nodes), args.partition_size)]

print("Writing partitions.")
for i, partition in enumerate(partitions):
    filename = "partition_{}_labeled_nodes.pickle".format(i)
    with open(join(args.output_dir, filename), "wb") as pickle_file:
        dump([node._id for node in partition], pickle_file)
