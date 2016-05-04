from collections import namedtuple
from itertools import chain, product
from os.path import isfile
from os import remove, popen
import sqlite3

from scipy.stats import gamma
import numpy as np
import pyximport; pyximport.install()

from common_segments import common_segment_lengths
from population_genomes import generate_genomes
from population_statistics import ancestors_of
from gamma import fit_gamma

GammaParams = namedtuple("GammaParams", ["shape", "scale"])

DB_FILE = "/media/paul/Storage/scratch/lengths.db"

cpu_info = dict([x.strip() for x in line.split(":")]
                for line in popen('lscpu').readlines())
try:
    NUM_CPU = int(cpu_info["Socket(s)"]) * int(cpu_info["Core(s) per socket"])
except KeyError:
    NUM_CPU = 1

class LengthClassifier:
    """
    Classifies based total length of shared segments
    """
    def __init__(self, population, labeled_nodes, genome_generator,
                 recombinators, min_segment_length = 0):
        self._distributions = dict()
        labeled_nodes = set(labeled_nodes)
        self._labeled_nodes = labeled_nodes
        unlabeled_nodes = chain.from_iterable(generation.members
                                              for generation
                                              in population.generations[-3:])
        unlabeled_nodes = set(unlabeled_nodes) - labeled_nodes
        con = _set_up_sqlite(DB_FILE)
        print("Finding related pairs.")
        pairs = related_pairs(unlabeled_nodes, labeled_nodes)
        print("{} related pairs.".format(len(pairs)))
        print("Calculating shared lengths.")
        for i in range(1000):
            print("iteration {}".format(i))
            print("Cleaning genomes.")
            population.clean_genomes()
            print("Generating genomes")
            generate_genomes(population, genome_generator, recombinators, 3)
            print("Calculating shared length")
            calculate_shared_to_db(pairs, con)
            con.commit()
        
        print("Generating distributions")
        self._distributions = calculate_distributions(pairs, con)

            
    def get_probability(self, shared_length, query_node, labeled_node):
        """
        Returns the probability that query_node and labeled_node have total
        shared segment length shared_length
        """
        shape, scale =  self._distributions[query_node, labeled_node]
        return gamma.pdf(shared_length, a = shape, scale = scale)

def related_pairs(unlabeled_nodes, labeled_nodes, generations = 7):
    """
    Given a population and labeled nodes, returns a list of pairs of nodes
    (unlabeled node, labeled node)
    where the labeled node and unlabeled node share at least 1 common ancestor
    within generation generations.
    """
    if type(labeled_nodes) != set:
        labeled_nodes = set(labeled_nodes)
    ancestors = dict()
    for node in chain(unlabeled_nodes, labeled_nodes):
        ancestors[node] = ancestors_of(node, generations)
    return [(unlabeled, labeled) for unlabeled, labeled
            in product(unlabeled_nodes, labeled_nodes)
            if len(ancestors[unlabeled].intersection(ancestors[labeled])) == 0]
        
        

def calculate_shared_to_db(pairs, con, min_segment_length = 0):
    """
    Calculate the shared segment lengths of each pair in pairs and
    store it in the given databse.
    Pairs are (unlabeled node, labeled node) pairs.
    """
    cur = con.cursor()
    shared_iter = ((unlabeled._id, labeled._id,
                    shared_segment_length_genomes(unlabeled.genome,
                                                  labeled.genome,
                                                  min_segment_length))
                   for unlabeled, labeled in pairs)
    cur.executemany("INSERT INTO lengths VALUES (?, ?, ?)", shared_iter)
    cur.execute("VACUUM")
    cur.close()

def calculate_distributions(pairs, con):
    cur = con.cursor()
    distributions = dict()
    for unlabeled, labeled in pairs:
            query = cur.execute("""SELECT shared
                                   FROM lengths
                                   WHERE unlabeled = ? AND labeled = ?""",
                                (unlabeled._id, labeled._id))
            lengths = np.fromiter((value[0] for value in query),
                                  dtype = np.float64)
            shape, scale = fit_gamma(lengths)
            params = GammaParams(shape, scale)
            distributions[(unlabeled, labeled)] = params
    cur.close()
    return distributions

def _set_up_sqlite(filename):
    if isfile(filename): # Clear old versions of this file
        remove(filename)
    temp_storage = sqlite3.connect(filename)
    temp_storage.execute("""PRAGMA page_size = 32768""");
    temp_storage.execute("""CREATE TABLE lengths
                            (unlabeled integer, labeled integer, shared integer)""")
    temp_storage.execute("""CREATE INDEX labeled_index
                            ON lengths (labeled)""")
    temp_storage.commit()
    return temp_storage
    
def shared_segment_length_genomes(genome_a, genome_b, minimum_length):
    lengths = common_segment_lengths(genome_a, genome_b)
    seg_lengths = (x for x in lengths if x >= minimum_length)
    return sum(seg_lengths)
    
def _shared_segment_length(node_a, node_b, minimum_length):
    return shared_segment_length_genomes(node_a.genome, node_b.genome,
                                          minimum_length)
