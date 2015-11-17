import re
import csv

from itertools import tee, izip
from os import listdir
from random import uniform, randint
from bisect import bisect_left

import numpy as np

MEGABASE = 10 ** 6

class RecombGenomeGenerator():
    def __init__(self, chromosome_lengths):
        self._chromosome_lengths = chromosome_lengths
        self._genome_id = 0

    def generate(self):
        chromosomes = dict()
        for chromosome, length in self._chromosome_lengths.items():
            mother = [(0, length, self._genome_id)]
            self._genome_id += 1
            father = [(0, length, self._genome_id)]
            self._genome_id += 1
            chromosomes[chromosome] = Autosome(mother, father)
            
        return RecombGenome(chromosomes)

class Autosome():
    """
    Encapsulates both homologs of a given Autosome.
    """
    def __init__(self, mother, father):
        self._mother = mother
        self._father = father

    @property
    def mother(self):
        return self._mother

    @property
    def father(self):
        return self._father


class RecombGenome():
    
    def __init__(self, chromosomes):
        self._chromsomes = chromosomes

    @property
    def chromosomes(self):
        return self._chromosomes

def recombinator_from_directory(directory):
    """
    Given a directory of files downloaded from, returns a Recombinator
    object for those files.
    http://hapmap.ncbi.nlm.nih.gov/downloads/recombination/
    """
    chromosomes = dict()
    for filename in listdir(directory):
        match = re.search("genetic_map_chr([0-9]+)_b36.txt", filename)
        if not match:
            continue
        chromosomes[int(match.group(1))] = filename
    return recombinator_from_files(chromosomes)

def recombinator_from_files(files):
    """
    Files is a dict from chromosomes to file names with mapping data
    for that chromosome.
    """
    chrom_data = dict()
    for chrom, filename in files.items():
        data = _read_recombination_file(filename)
        chrom_data[chrom] = data
    return Recombinator(chrom_data)

def _read_recombination_file(filename):
    rows = []
    with open(filename, "r") as chrom_file:
        # XXX Use csv here instead?
        chrom_file.readline() # throw out header
        for row in chrom_file:
            row = row.strip().split(" ")
            row[0] = int(row[0])
            row[1] = float(row[1])
            row[2] = int(row[2])
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
            chromosome = int(line[0])
            male_length = float(line[4])
            female_length = float(line[5])
            male_lengths[chromosome] = male_length
            female_lengths[chromosomes] = female_length
    return {"male": male_lengths, "female": female_lengths}

def pairwise(iterable):
    """
    From https://docs.python.org/3.4/library/itertools.html#itertools-recipes
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    """
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def remap_recombinator(recombinator, chrom_lengths):
    # TODO: write this function to remap a Recombinator into a sex based recombinator
    pass
        
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
        loci = []
        for location in recomb_locations:
            index = bisect_left(self._end_points[chrom], location)
            end_point = self._end_points[chrom][index]
            loci.append(randint(*self._end_point_range[end_point]))
        return loci

    def recombination(self, genome):
        new_autosomes = dict()
        for chrom_name, autosome in genome.chromosomes.items():
            locations = self._recombination_locations(self, chrom_name)
            if len(locations) % 2 == 1:
                locations.append(self._num_bases[chrom_name])
            # The zip is the pairs of adjecent list members.
            # eg if x = [0, 1, 2, 3], then zip(x[::2], x[1::2]) is an iterable
            # that yields (0, 1) then (2, 3)
            for location in zip(locations[::2], locations[1::2]):
                mother_location = bisect_left(autosome.mother, location)
                father_location = bisect_left(autosome.father, location)
                # TODO: Finish this.
