from collections import deque, defaultdict, namedtuple
from itertools import chain, product
from os.path import isfile
from os import remove, popen
from functools import partial
from multiprocessing import Pool
import sqlite3

from scipy.stats import gamma
import numpy as np
import pyximport; pyximport.install()

from common_segments import common_segment_lengths
from population_genomes import generate_genomes
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
        cur = con.cursor()

        # Setup for parallelism
        partitioned_labeled = _partition_labeled_nodes(labeled_nodes)
        parallel_shared = partial(_pairwise_shared,
                                unlabeled_nodes = unlabeled_nodes,
                                min_segment_length = min_segment_length)
                                
        for i in range(1000):
            print("iteration {}".format(i))
            print("Cleaning genomes.")
            population.clean_genomes()
            print("Generating genomes")
            generate_genomes(population, genome_generator, recombinators, 3)
            print("Calculating shared length")
            with Pool(NUM_CPU) as p:
                lengths_iter = p.imap_unordered(parallel_shared,
                                                partitioned_labeled)
                chain_lengths = chain.from_iterable(lengths_iter)
                cur.executemany("INSERT INTO lengths VALUES (?, ?, ?)",
                                chain_lengths)
            con.commit()
        cur.execute("VACUUM")
        cur.close()
        
        print("Generating distributions")
        parallel_params = partial(_fit_distributions,
                                  unlabeled_nodes = unlabeled_nodes)
        mapping = next(iter(labeled_nodes)).mapping
        with Pool(NUM_CPU) as p:
            params = chain.from_iterable(p.imap_unordered(parallel_params,
                                                          partitioned_labeled))
            self._distributions = {(mapping[pair[0]],
                                    mapping[pair[1]]): parameters
                                   for pair, parameters in params}


            
    def get_probability(self, shared_length, query_node, labeled_node):
        """
        Returns the probability that query_node and labeled_node have total
        shared segment length shared_length
        """
        shape, scale =  self._distributions[query_node, labeled_node]
        return gamma.pdf(shared_length, a = shape, scale = scale)

def calculate_shared_to_db(labeled_nodes, unlabeled_nodes, database_name,
                     min_segment_length = None):
    """
    Calculate the shared segment lengths of each pair in
    product(labeled_nodes, unlabeled_nodes) and store it in the given databse
    """
    if isfile(database_name):
        con = sqlite3.connect(databse_name)
    else:
        con = _set_up_sqlite(database_name)
    cur = con.cursor()
    shared_iter = ((unlabeled._id, labeled._id,
                    shared_segment_length_genomes(unlabeled.genome,
                                                  labeled.genome,
                                                  min_segment_length))
                   for labeled, unlabeled
                   in product(labeled_nodes, unlabeled_nodes))
    cur.executemany("INSERT INTO lengths VALUES (?, ?, ?)", shared_iter)
    cur.execute("VACUUM")
    cur.close()

def calculate_distributions(labeled_nodes, unlabeled_nodes, database_name):
    db_connection = sqlite3.connect(database_name)
    cur = db_connection.cursor()
    distributions = dict()
    for unlabeled, labeled in product(unlabeled_nodes, labeled_nodes):
            query = cur.execute("""SELECT shared
                                   FROM lengths
                                   WHERE unlabeled = ? AND labeled = ?""",
                                (unlabeled._id, labeled._id))
            lengths = np.fromiter((value[0] for value in query),
                                  dtype = np.float64)
            shape, scale = fit_gamma(lengths)
            params = GammaParams(shape, scale)
            distributions[(unlabeled._id, labeled._id)] = params
    cur.close()
    db_connection.close()
    return ret_values

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

def _pairwise_shared(labeled_nodes, unlabeled_nodes, min_segment_length):
    return [(unlabeled._id, labeled._id,
             shared_segment_length_genomes(unlabeled.genome,
                                           labeled.genome,
                                           min_segment_length))
            for labeled, unlabeled
            in product(labeled_nodes, unlabeled_nodes)]

def _fit_distributions(labeled_nodes, unlabeled_nodes):
    db_connection = sqlite3.connect(DB_FILE)
    cur = db_connection.cursor()
    ret_values = []
    for unlabeled, labeled in product(unlabeled_nodes, labeled_nodes):
            query = cur.execute("""SELECT shared
                                   FROM lengths
                                   WHERE unlabeled = ? AND labeled = ?""",
                                (unlabeled._id, labeled._id))
            lengths = np.fromiter((value[0] for value in query),
                                  dtype = np.float64)
            shape, scale = fit_gamma(lengths)
            params = GammaParams(shape, scale)
            pair = (unlabeled._id, labeled._id)            
            ret_values.append((pair, params))
    cur.close()
    db_connection.close()
    return ret_values
def _partition_labeled_nodes(labeled_nodes):
    """
    Partitions labeled nodes into equally sized sets
    The number of sets is roughly twice the number of CPUs.
    """
    l = list(labeled_nodes)
    partition_size = len(l) // (NUM_CPU * 8)
    return [l[i:i+ partition_size] for i in range(0, len(l), partition_size)]
    
def shared_segment_length_genomes(genome_a, genome_b, minimum_length):
    by_autosome = common_segment_lengths(genome_a, genome_b)
    seg_lengths = filter(lambda x: x >= minimum_length,
                         chain.from_iterable(by_autosome.values()))
    return sum(seg_lengths)
    
def _shared_segment_length(node_a, node_b, minimum_length):
    return shared_segment_length_genomes(node_a.genome, node_b.genome,
                                          minimum_length)

def _founders(node):
    assert node is not None
    nodes = deque([node])
    founders = set()
    while len(nodes) > 0:
        node = nodes.pop()
        if node.mother is None:
            assert node.father is None
            founders.add(node)
        else:
            nodes.appendleft(node.mother)
            nodes.appendleft(node.father)
    return founders
    
