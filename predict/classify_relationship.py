from collections import deque, defaultdict
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

DB_FILE = "/media/paul/Storage/scratch/lengths_profile.db"

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
        labeled_nodes_l = list(labeled_nodes)
        unlabeled_nodes = chain.from_iterable(generation.members
                                              for generation
                                              in population.generations[-3:])
        unlabeled_nodes = set(unlabeled_nodes) - labeled_nodes
        con = self._set_up_sqlite()
        cur = con.cursor()
        parallel_func = partial(_parallel_pairwise,
                                unlabeled_nodes = unlabeled_nodes,
                                min_segment_length = min_segment_length)
                                
        for i in range(3):
            print("iteration {}".format(i))
            print("Cleaning genomes.")
            population.clean_genomes()
            print("Generating genomes")
            generate_genomes(population, genome_generator, recombinators, 3)
            print("Calculating shared length")
            partition_size = len(labeled_nodes_l) // (NUM_CPU * 2)
            chunked_labeled = [labeled_nodes_l[i:i+ partition_size] for i
                               in range(0, len(labeled_nodes_l),
                                        partition_size)]
            with Pool(NUM_CPU) as p:
                lengths_iter = chain.from_iterable(p.imap(parallel_func,
                                                          chunked_labeled))
                cur.executemany("INSERT INTO lengths VALUES (?, ?, ?)",
                                lengths_iter)
            con.commit()
        # print("Generating distributions")
        # for unlabeled, labeled in product(unlabeled_nodes, labeled_nodes):
        #     query = cur.execute("""SELECT shared
        #                            FROM lengths
        #                            WHERE unlabeled = ? AND labeled = ?""",
        #                         (unlabeled._id, labeled._id))
        #     lengths = [value[0] for value in query]
        #     self._distributions[unlabeled, labeled] = gamma(*gamma.fit(lengths))
        cur.close()
            
    def _set_up_sqlite(self):
        if isfile(DB_FILE): # Clear old versions of this file
            remove(DB_FILE)
        temp_storage = sqlite3.connect(DB_FILE)
        temp_storage.execute("""PRAGMA page_size = 32768""");
        temp_storage.execute("""CREATE TABLE lengths
                                (unlabeled integer, labeled integer, shared integer)""")
        temp_storage.execute("""CREATE INDEX labeled_index
                                ON lengths (labeled)""")
        temp_storage.commit()
        return temp_storage

            
    def get_probability(self, shared_length, query_node, labeled_node):
        """
        Returns the probability that query_node and labeled_node have total
        shared segment length shared_length
        """
        return self._distributions[query_node, labeled_node].pdf(shared_length)

def _parallel_pairwise(labeled_nodes, unlabeled_nodes, min_segment_length):
    return [(unlabeled._id, labeled._id,
             shared_segment_length_genomes(unlabeled.genome,
                                           labeled.genome,
                                           min_segment_length))
            for unlabeled, labeled
            in product(unlabeled_nodes, labeled_nodes)]
    
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
    
