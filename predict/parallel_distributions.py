"""
This script is meant to be run across many machines, working together
to calculate a large number of shared length distributions.
"""
from argparse import ArgumentParser
from pickle import load
from os.path import join
from uuid import uuid4

from population import population_from_directory
from classify_relationship import calculate_shared_to_db

parser = ArgumentParser(description='Computed shared segements.')
parser.add_argument("population_dirname",
                    help = "Name of the pickle file storing the population")
parser.add_argument("labeled_filename",
                    help = "Name of the pickle file with the ids of the labeled nodes")
parser.add_argument("work_dir", help = "directory to store intermediate data, and to store output files.")
parser.add_argument("--database", default = None,
                    help = "name of sqlite database to use.")
args = parser.parse_args()

if args.database is None:
    db_name  = join(args.work_dir, "lengths_" + str(uuid4()) + ".db")
else:
    db_name = join(args.work_dir, args.database)

print("Loading population")
population = population_from_directory(args.population_dirname)

with open(args.labeled_filename, "rb") as pickle_file:
    labeled_node_ids = load(pickle_file)
    
mapping = population.id_mapping
labeled_nodes = set(mapping[node_id] for node_id in labeled_node_ids)
unlabeled_nodes = [node for node in population.members if node.genome is not None]

print("Calculating shared length of nodes in {}".format(args.labeled_filename))
calculate_shared_to_db(labeled_nodes, unlabeled_nodes, db_name)
print("Distributions for {} calculated".format(args.labeled_filename))
