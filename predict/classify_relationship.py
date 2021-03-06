from collections import namedtuple, defaultdict
from itertools import chain, product
from os import popen, listdir, makedirs
from os.path import join, exists
from shutil import rmtree
from warnings import warn

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
    def __init__(self, distributions, labeled_nodes):
        self._distributions = distributions
        self._labeled_nodes = labeled_nodes

            
    def get_probability(self, shared_length, query_node, labeled_node):
        """
        Returns the probability that query_node and labeled_node have total
        shared segment length shared_length
        """
        shape, scale =  self._distributions[query_node, labeled_node]
        return gamma.pdf(shared_length, a = shape, scale = scale)

    def fix_persistence(self, population):
        """
        This is a hack, because pickling causes issues. Long term
        should probably use something from
        https://docs.python.org/3/library/pickle.html#pickle-persistent
        """
        id_map = population.id_mapping
        self._distributions = {(id_map[nodes[0]._id],
                                id_map[nodes[1]._id]): dist
                               for nodes, dist
                               in self._distributions.items()}
        self._labeled_nodes = [id_map[node._id] for node in self._labeled_nodes]

    def __contains__(self, item):
        return item in self._distributions

def related_pairs(unlabeled_nodes, labeled_nodes, population, generations):
    """
    Given a population and labeled nodes, returns a list of pairs of nodes
    (unlabeled node, labeled node)
    where the labeled node and unlabeled node share at least 1 common ancestor
    going back generation generations from the latest generation.
    """
    generation_map = population.node_to_generation
    num_generations = population.num_generations
    if type(labeled_nodes) != set:
        labeled_nodes = set(labeled_nodes)
    ancestors = dict()
    for node in chain(unlabeled_nodes, labeled_nodes):
        node_generation = generation_map[node]
        from_latest = (num_generations - node_generation - 1)
        generations_back =  generations - from_latest
        ancestors[node] = ancestors_of(node, generations_back)
    return [(unlabeled, labeled) for unlabeled, labeled
            in product(unlabeled_nodes, labeled_nodes)
            if len(ancestors[unlabeled].intersection(ancestors[labeled])) != 0]


def generate_classifier(population, labeled_nodes, genome_generator,
                        recombinators, directory, clobber = True,
                        iterations = 1000, generations_back_shared = 7):    
    if not exists(directory):
        makedirs(directory)
    elif clobber:
        rmtree(directory)
        makedirs(directory)
    shared_to_directory(population, labeled_nodes, genome_generator,
                        recombinators, directory, clobber = clobber,
                        iterations = iterations,
                        generations_back_shared = generations_back_shared)
    return classifier_from_directory(directory, population.id_mapping)


def shared_to_directory(population, labeled_nodes, genome_generator,
                        recombinators, directory, min_segment_length = 0,
                        clobber = True, iterations = 1000,
                        generations_back_shared = 7):

    labeled_nodes = set(labeled_nodes)
    unlabeled_nodes = chain.from_iterable(generation.members
                                          for generation
                                          in population.generations[-3:])
    unlabeled_nodes = set(unlabeled_nodes) - labeled_nodes
    print("Finding related pairs.")
    pairs = related_pairs(unlabeled_nodes, labeled_nodes, population,
                          generations_back_shared)
    print("{} related pairs.".format(len(pairs)))
    print("Opening file descriptors.")
    if clobber:
        mode = "w"
    else:
        mode = "a"
    fds = {node: open(join(directory, str(node._id)), mode)
           for node in labeled_nodes}
    print("Calculating shared lengths.")
    for i in range(iterations):
        print("iteration {}".format(i))
        print("Cleaning genomes.")
        population.clean_genomes()
        print("Generating genomes")
        generate_genomes(population, genome_generator, recombinators, 3)
        print("Calculating shared length")
        _calculate_shared_to_fds(pairs, fds, min_segment_length)
    for fd in fds.values():
        fd.close()
        
def _calculate_shared_to_fds(pairs, fds, min_segment_length):
    """
    Calculate the shared length between the pairs, and store the
    shared length in the given directory. Each labeled node has a file
    in the given directory. The files contain tab separated entries,
    where the first entry is the unlabeled node id, and the second
    entry is the amount of shared material.
    """
    shared_iter = ((unlabeled, labeled,
                    shared_segment_length_genomes(unlabeled.genome,
                                                  labeled.genome,
                                                  min_segment_length))
                   for unlabeled, labeled in pairs)
    for unlabeled, labeled, shared in shared_iter:
        fd = fds[labeled]
        fd.write(str(unlabeled._id))
        fd.write("\t")
        fd.write(str(shared) + "\n")

def classifier_from_directory(directory, id_mapping):
    distributions = distributions_from_directory(directory, id_mapping)
    labeled_nodes = set(id_mapping[int(filename)]
                        for filename in listdir(directory))
    return LengthClassifier(distributions, labeled_nodes)

def distributions_from_directory(directory, id_mapping):
    """
    Calculate distributions from a directory created by
    calculate_shared_to_directory.
    """
    distributions = dict()
    for labeled_filename in listdir(directory):
        lengths = defaultdict(list)
        labeled = id_mapping[int(labeled_filename)]
        with open(join(directory, labeled_filename), "r") as labeled_file:
            for line in labeled_file:
                # If the program crashed, the output can be left in an
                # inconsistent state.
                try:
                    unlabeled_id, shared_str = line.split("\t")
                except ValueError:
                    warn("Malformed line:\n{}".format(line), stacklevel = 0)
                    continue
                try:
                    unlabeled = id_mapping[int(unlabeled_id)]
                except KeyError:
                    error_string = "No such unlabeled node with id {}."
                    warn(error_string.format(unlabeled_id), stacklevel = 0)
                    continue
                lengths[unlabeled].append(int(shared_str))
        for unlabeled, lengths in lengths.items():
            shape, scale = fit_gamma(np.array(lengths, dtype = np.float64))
            params = GammaParams(shape, scale)
            distributions[unlabeled, labeled] = params
    return distributions
    
def shared_segment_length_genomes(genome_a, genome_b, minimum_length):
    lengths = common_segment_lengths(genome_a, genome_b)
    seg_lengths = (x for x in lengths if x >= minimum_length)
    return sum(seg_lengths)
    
def _shared_segment_length(node_a, node_b, minimum_length):
    return shared_segment_length_genomes(node_a.genome, node_b.genome,
                                          minimum_length)
