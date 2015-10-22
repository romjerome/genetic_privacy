class RecombGenomeGenerator():
    def __init__(self, chromosome_lengths):
        self._chromosome_lengths = chromosome_lengths
        self._genome_id = 0

    def generate(self):
        chromosomes = dict()
        for chromosome, length in self._chromosome_lengths.items():
            chromosomes[chromosome] = [(0, length, self._genome_id)]
        
        self._genome_id += 1
        return RecombGenome(chromosomes)
            

class RecombGenome():
    def __init__(self, chromosomes):
        pass
