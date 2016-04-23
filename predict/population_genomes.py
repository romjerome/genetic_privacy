from collections import deque
from random import random

from sex import Sex
from recomb_genome import Autosome, RecombGenome

def mate(mother, father, mother_recombinator, father_recombinator):
    """
    Takes a mother and father, and returns a genome for a child
    """
    assert mother is not None
    assert father is not None
    mother_recomb = mother_recombinator.recombination(mother)
    father_recomb = father_recombinator.recombination(father)
    offspring_autosomes = dict()
    num_founders = mother._num_founders
    for chrom_name, chromosome in mother_recomb.chromosomes.items():
        # TODO: Don't clobber mother and father references.
        if random() < 0.5:
            mother = mother_recomb.chromosomes[chrom_name].mother
        else:
            mother = mother_recomb.chromosomes[chrom_name].father
        if random() < 0.5:
            father = father_recomb.chromosomes[chrom_name].mother
        else:
            father = father_recomb.chromosomes[chrom_name].father
        offspring_autosomes[chrom_name] = Autosome(mother, father)
    return RecombGenome(offspring_autosomes, num_founders)

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
        if keep_last is not None and keep_last < generation_num:
            to_delete = population.generations[generation_num - keep_last]
            for person in to_delete.members:
                del person.genome
    if keep_last is not None:
        population._generations_with_genomes = keep_last
    else:
        population._generations_with_genomes = population.num_generations
