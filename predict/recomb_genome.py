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

def recombinator_from_files(files):
    """
    Files is a dict from chromosomes to file names with mapping data
    for that chromosome.
    """
    for chrom, filename in files.items():
        with open(filename, "r") as chrom_file:
            pass

class Recombinator():
    def __init__(self):
        pass

    def recombination(self, genome):
        pass

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

def recombine_genome(genome, recomb_map):
    pass
