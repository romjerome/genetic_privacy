from bisect import bisect_left
from collections import deque
from random import random

import numpy as np

from sex import Sex
from recomb_genome import RecombGenome, Diploid, CHROMOSOME_ORDER

def _pick_chroms_for_diploid(genome, recombinator):
    """
    Takes a genome and returns a diploid chromosome that is the result
    of recombination events and randomly picking a diploid for each
    autosome.
    """
    recomb_genome = recombinator.recombination(genome)
    mother = recomb_genome.mother
    father = recomb_genome.father
    starts = []
    founder = []
    offsets = recombinator._chrom_start_offset
    for chrom_name in CHROMOSOME_ORDER:
        if random() < 0.5:
            tmp_diploid = mother
        else:
            tmp_diploid = father

        chrom_start = bisect_left(tmp_diploid.starts, offsets[chrom_name])
        if chrom_name != CHROMOSOME_ORDER[-1]:
            chrom_stop = bisect_left(tmp_diploid.starts,
                                     offsets[chrom_name + 1])
        else:
            chrom_stop = len(tmp_diploid.starts)
                
        starts.extend(tmp_diploid.starts[chrom_start:chrom_stop])
        founder.extend(tmp_diploid.founder[chrom_start:chrom_stop])
    return Diploid(np.array(starts, dtype = np.uint32),
                   mother.end,
                   np.array(founder, dtype = np.uint32))


def mate(mother, father, mother_recombinator, father_recombinator):
    """
    Takes a mother and father, and returns a genome for a child
    """
    assert mother is not None
    assert father is not None
    from_mother = _pick_chroms_for_diploid(mother, mother_recombinator)
    from_father = _pick_chroms_for_diploid(father, father_recombinator)
    num_founders = mother._num_founders
    return RecombGenome(from_mother, from_father, num_founders)

def generate_genomes_ancestors(root_nodes, generator, recombinators):
    queue = deque(root_nodes)
    visited = set()
    while len(queue) > 0:
        person = queue.popleft()
        if person in visited:
            continue
        if person.mother is not None:
            assert person.father is not None
            if person.mother not in visited or person.father not in visited:
                continue
            person.genome =  mate(person.mother.genome, person.father.genome,
                                  recombinators[Sex.Female],
                                  recombinators[Sex.Male])
        else:
            person.genome = generator.generate()
        queue.extend(person.children)
        visited.add(person)

def generate_genomes(population, generator, recombinators, keep_last = None):
    assert keep_last is None or keep_last > 0
    for generation_num, generation in enumerate(population.generations):
        for person in generation.members:
            if person.genome is not None:
                continue
            mother = person.mother
            father = person.father
            if mother is None:
                person.genome = generator.generate()
                continue
            assert mother.genome is not None
            assert father.genome is not None
            person.genome = mate(mother.genome, father.genome,
                                 recombinators[Sex.Female],
                                 recombinators[Sex.Male])
        if keep_last is not None and keep_last <= generation_num:
            to_delete = population.generations[generation_num - keep_last]
            for person in to_delete.members:
                del person.genome
    if keep_last is not None:
        population._generations_with_genomes = keep_last
    else:
        population._generations_with_genomes = population.num_generations
