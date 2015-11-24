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
    for chrom_name, chromosome in mother_recomb.chromosomes.items():
        if random() < 0.5:
            mother = mother_recomb.chromosomes[chrom_name].mother
        else:
            mother = mother_recomb.chromosomes[chrom_name].father
        if random() < 0.5:
            father = father_recomb.chromosomes[chrom_name].mother
        else:
            father = father_recomb.chromosomes[chrom_name].father
        offspring_autosomes[chrom_name] = Autosome(mother, father)
    return RecombGenome(offspring_autosomes)

def generate_genomes(population, generator, recombinators):
    # I don't use recursion because python doesn't do well with
    # deep recursion
    queue = deque(population.generations[0].members)
    while len(queue) > 0:
        person = queue.popleft()
        if person.genome is not None:
            continue
        # An optimization would be to only add children if person is female
        # This way people only go into the queue once.
        queue.extend(person.children)
        mother = person.mother
        father = person.father
        if mother is None:
            person.genome = generator.generate()
            continue
        assert mother.genome is not None
        assert father.genome is not None
        person.genome = mate(mother.genome, father.genome,
                             recombinators[Sex.Female], recombinators[Sex.Male])
