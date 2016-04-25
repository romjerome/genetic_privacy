3
import re
import csv

from array import array
from itertools import tee
from os import listdir
from os.path import isfile, join
from random import uniform
from bisect import bisect_left
from collections import defaultdict, namedtuple
from itertools import chain

import numpy as np

from sex import Sex

MEGABASE = 10 ** 6
DECODE_FILENAME = "decode_recombination_data.tab"
CHROMOSOME_ORDER = list(range(1, 23))

Diploid = namedtuple("Diploid", ["starts", "stops", "founder"])
IndexMap = namedtuple("IndexMap", ["mother", "father"])

class RecombGenomeGenerator():
    def __init__(self, chromosome_lengths, num_founders):
        self._chromosome_lengths = chromosome_lengths
        self._total_length = sum(chromosome_lengths.values())
        self._num_founders = num_founders
        self._genome_id = 0

    def generate(self):
        assert self._genome_id < 2 * self._num_founders
        
        mother = Diploid(array("L", [0]), array("L", [self._total_length]),
                         array("L", [self._genome_id]))
        father = Diploid(array("L", [0]), array("L", [self._total_length]),
                         array("L", [self._genome_id + 1]))
        
        self._genome_id += 2
        return RecombGenome(mother, father, self._num_founders)

class RecombGenome():
    
    def __init__(self, mother, father, num_founders):
        self.mother = mother
        self.father = father
        self._num_founders = num_founders
        extract = self._extract_founder_bits_and_map(mother, father)
        self._founder_bits, self._index_map = extract
            
    def _extract_founder_bits_and_map(self, mother, father):
        founder_bits = np.zeros(self._num_founders * 2, dtype = np.uint8)
        founder_bits[mother.founder] = 1
        founder_bits[father.founder] = 1

        mother_map = defaultdict(list)
        father_map = defaultdict(list)
        # index_map = IndexMap(, defaultdict(list))
        for index, founder in enumerate(mother.founder):
            mother_map[founder].append(index)
        for index, founder in enumerate(father.founder):
            father_map[founder].append(index)

        # Compact things using smaller data structures
        mother_map = {founder: array("L", mother_map[founder])
                      for founder in mother_map}
        father_map = {founder: array("L", father_map[founder])
                      for founder in father_map}
        index_map = IndexMap(mother_map, father_map)
        
        return (np.packbits(founder_bits), index_map)

def recombinators_from_directory(directory):
    """
    Given a directory of files downloaded from, returns a Recombinator
    object for those files.
    Genome maps are from
    http://hapmap.ncbi.nlm.nih.gov/downloads/recombination/
    Sex based centimorgan lengths are from decode doi:10.1038/ng917.
    """
    chromosomes = dict()
    for filename in listdir(directory):
        match = re.search("genetic_map_chr([0-9]+)_b36.txt", filename)
        if not match:
            continue
        chromosomes[int(match.group(1))] = join(directory, filename)
    decode_file = join(directory, DECODE_FILENAME)
    if isfile(decode_file):
        sex_data = read_sex_lengths(decode_file)
    return recombinators_from_hapmap_files(chromosomes, sex_data)

def recombinators_from_hapmap_files(hapmap_files, sex_lengths = None):
    """
    Files is a dict from chromosomes to file names with mapping data
    for that chromosome.
    """
    chrom_data = dict()
    for chrom, filename in hapmap_files.items():
        chrom_data[chrom] = _read_recombination_file(filename)
    if not sex_lengths:
        return Recombinator(chrom_data)

    # We may need to interpolate the data to the different rates for
    # the sexes. This may need to be replaced with something more
    # sophisticated later.
    sex_adjusted_data = defaultdict(dict)
    for sex, sex_lengths in sex_lengths.items():
        for chromosome, length in sex_lengths.items():
            original_length = chrom_data[chromosome][-1][2]
            ratio = length / original_length
            data = chrom_data[chromosome]
            sex_adjusted_data[sex][chromosome] = _adjust_centimorgans(data,
                                                                      ratio)
    return {sex: Recombinator(data) for sex, data in sex_adjusted_data.items()}

def _adjust_centimorgans(rows, multiplier = 1.0):
    """
    Adjusts the number of centimorgans in rows by some multiplier.
    eg if we have the rows

    a 0.05 0
    b 0.1  0.05
    c 0.05 0.15

    and we apply a multiplier of 2, then we are doubling the number of
    centimorgans, giving us.

    a 0.1 0
    b 0.2 0.1
    c 0.1 0.3
    """
    return [(bp, rate * multiplier, distance * multiplier)
            for bp, rate, distance in rows]

def _read_recombination_file(filename):
    """
    Reads a recombination file and returns the rows, with columns
    converted to the appropriate numeric types.
    """
    rows = []
    with open(filename, "r") as chrom_file:
        # XXX Use csv here instead?
        chrom_file.readline() # throw out header
        for row in chrom_file:
            row = row.strip().split(" ")
            row[0] = int(row[0])
            row[1] = float(row[1])
            row[2] = float(row[2])
            rows.append(row)
    return rows

def _inverse_cumulative_sum(x):
    """
    Given some vector x which is the cumulative sum of another vector
    y, returns y.
    http://stackoverflow.com/a/16541726/300539
    """
    return np.cumsum(x[::-1])[::-1]

def read_sex_lengths(filename):
    """
    Read in file from decode paper that has the centimorgan length of
    chromosomes by sex. Stored at
    https://github.com/citp/genetic_privacy/blob/master/data/recombination_rates/decode_recombination_data.tab
    """
    male_lengths = dict()
    female_lengths = dict()
    with open(filename) as csv_file:
        reader = csv.reader(csv_file, delimiter = "\t")
        next(reader) # get rid of header
        for line in reader:
            if line[0].lower() == "x" or line[0].lower() == "y":
                continue
            chromosome = int(line[0])
            male_length = float(line[4])
            female_length = float(line[5])
            male_lengths[chromosome] = male_length
            female_lengths[chromosome] = female_length
    return {Sex.Male: male_lengths, Sex.Female: female_lengths}

def pairwise(iterable):
    """
    From https://docs.python.org/3.4/library/itertools.html#itertools-recipes
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
        
class Recombinator():
    def __init__(self, recombination_data):
        """
        recombination_data is list of position, cM / Mb, (cumulative)
        cM values, as given by the hapmap data file.
        """
        # Maps chromosome to the number of bases in the chromosome
        self._num_bases = dict()
        # Maps chromosome to the number of centimorgans in the chromosome
        self._num_centimorgans = dict()
        # The end points of each contiguous segment of bases that
        # share a recombination rate, measured in cumulative
        # centimorgans.
        # For example if the chromosome file has the lines
        # 554484 0.0015000000 0.0007230750
        # 555296 0.0015000000 0.0007242930
        # Then the end point for 554484-555296 will be 0.0007242930
        self._end_points = dict()
        # Maps end points to their ranges.
        self._end_point_range  = dict()
        for chrom, data in recombination_data.items():
            self._num_bases[chrom] = data[-1][0]
            self._num_centimorgans[chrom] = data[-1][2]
            end_points = [row[2] for row in data[1:]]
            self._end_points[chrom] = end_points
            range_lookup = dict()
            for l_1, l_2 in pairwise(data):
                pos_1 = l_1[0]
                pos_2 = l_2[0]
                end_point = l_2[2]
                range_lookup[end_point] = (pos_1, pos_2)
            self._end_point_range[chrom] = range_lookup
        ordered_cum_bases = np.cumsum([self._num_bases[chrom]
                                      for chrom in CHROMOSOME_ORDER])
        self._chrom_start_offset = dict(zip(CHROMOSOME_ORDER,
                                            ordered_cum_bases))

    def _recombination_locations(self, chrom):
        """
        Given a chromosome name, returns a list of locations where
        recombination events could happen based on monte carlo
        methods.

        This is done by first sampling from a binomial distribution to
        determine the number of recombination events, then repeatedly
        selecting values uniformly from 0 to the number of
        centimorgans in a chromosome to determine where the
        recombination events occur.
        """
        bases = self._num_bases[chrom]
        centimorgans = self._num_centimorgans[chrom]
        recomb_events = np.random.binomial(bases,
                                           (centimorgans * 0.01)/ bases)
        recomb_locations = [uniform(0, centimorgans)
                            for _ in range(recomb_events)]
        recomb_locations.sort()
        loci = []
        for location in recomb_locations:
            index = bisect_left(self._end_points[chrom], location)
            end_point = self._end_points[chrom][index]
            start, stop = self._end_point_range[chrom][end_point]
            if index == 0:
                start_point = 0.0
            else:
                start_point = self._end_points[chrom][index - 1]
            assert location > start_point
            # fraction_in is the fraction of the way into this region
            # the recombination event occurs.
            fraction_in = (location - start_point) / (end_point - start_point)
            recomb_spot = int((stop - start) * fraction_in + start)
            if len(loci) == 0 or recomb_spot != loci[-1]:
                loci.append(recomb_spot)
        return loci

    def recombination(self, genome):
        """
        Given a RecombGenome, returns a new RecombGenome object that
        is the product of recombination on the given RecombGenome.
        """
        assert genome is not None
        global_locations = []
        for chrom_name in CHROMOSOME_ORDER:
            locations = self._recombination_locations(chrom_name)
            if len(locations) % 2 == 1:
                locations.append(self._num_bases[chrom_name])
            # Adjust the locations for our global genome
            offset = self._chrom_start_offset[chrom_name]
            global_locations.extend(location + offset
                                    for location in locations)
            
        mother, father = _swap_at_locations(genome.mother,
                                            genome.father,
                                            zip(global_locations[::2],
                                                global_locations[1::2]))
                
        return RecombGenome(mother, father, genome._num_founders)

def _new_sequence(diploid, locations):
    """
    Return a new sequence, broken up at the given start, stop locations.
    Eg the sequence starts: 0  10 20
                    stops:  10 20 30
    passed with the locations [15, 25] should produce the sequence
                    starts: 0  10 15 20 25
                    stops:  10 15 20 25 30
    """
    non_duplicate = []
    for break_location in locations:
        if break_location == diploid.stops[-1]:
            continue
        break_index = bisect_left(diploid.starts, break_location)
        if (break_index == len(diploid.starts) or
            diploid.starts[break_index] != break_location):
            non_duplicate.append(break_location)
    return_starts = list(diploid.starts)
    return_starts.extend(non_duplicate)
    return_starts.sort()

    return_stops = return_starts[1:]
    return_stops.append(diploid.stops[-1])
    
    return_founder = []
    j = 0
    for i in range(len(return_starts)):
        if j < len(diploid.starts) and return_starts[i] == diploid.starts[j]:
            return_founder.append(diploid.founder[j])
            j += 1
        else:
            return_founder.append(diploid.founder[j - 1])

    return Diploid(return_starts, return_stops, return_founder)

def _swap_at_locations(mother, father, locations):
    """
    Swap elements at the given (start, stop) locations in locations.
    Locations is given by basepair locations, rather than centimorgans
    or list index.
    """
    locations = list(locations)
    new_mother = _new_sequence(mother, chain.from_iterable(locations))
    new_father = _new_sequence(father, chain.from_iterable(locations))
    for start, stop in locations:
        mother_start_i = bisect_left(new_mother.starts, start)
        mother_stop_i = bisect_left(new_mother.starts, stop)
        father_start_i = bisect_left(new_father.starts, start)
        father_stop_i = bisect_left(new_father.starts, stop)
        temp_mother = new_mother.starts[mother_start_i:mother_stop_i]
        temp_father = new_father.starts[father_start_i:father_stop_i]
        new_mother.starts[mother_start_i:mother_stop_i], \
            new_father.starts[father_start_i:father_stop_i] = (temp_father,
                                                               temp_mother)

        temp_mother = new_mother.stops[mother_start_i:mother_stop_i]
        temp_father = new_father.stops[father_start_i:father_stop_i]
        new_mother.stops[mother_start_i:mother_stop_i], \
            new_father.stops[father_start_i:father_stop_i] = (temp_father,
                                                              temp_mother)

        temp_mother = new_mother.founder[mother_start_i:mother_stop_i]
        temp_father = new_father.founder[father_start_i:father_stop_i]
        new_mother.founder[mother_start_i:mother_stop_i], \
            new_father.founder[father_start_i:father_stop_i] = (temp_father,
                                                                temp_mother)
    return_mother = Diploid(array("L", new_mother.starts),
                            array("L", new_mother.stops),
                            array("L", new_mother.founder))
    return_father = Diploid(array("L", new_father.starts),
                            array("L", new_father.stops),
                            array("L", new_father.founder))
    return (return_mother, return_father)
        
