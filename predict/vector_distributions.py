from collections import deque
import pdb

import numpy as np

from node import NodeGenerator
from sex import Sex
from population_genomes import mate
from recomb_genome import recombinators_from_directory, RecombGenomeGenerator
from classify_relationship import shared_segment_length_genomes

node_generator = NodeGenerator()

### <2, 4>
### First configuration, grandchild-grandparent

great_grandparent_0 = node_generator.generate_node(sex = Sex.Female)
great_grandparent_1 = node_generator.generate_node(sex = Sex.Male)
great_grandparent_2 = node_generator.generate_node(sex = Sex.Male)

grandparent_0 = node_generator.generate_node(great_grandparent_1,
                                             great_grandparent_0,
                                             Sex.Male)
grandparent_1 = node_generator.generate_node(great_grandparent_2,
                                             great_grandparent_0,
                                             Sex.Male)
grandparent_2 = node_generator.generate_node(sex = Sex.Female)
grandparent_3 = node_generator.generate_node(sex = Sex.Female)

parent_0 = node_generator.generate_node(grandparent_0,
                                        grandparent_2,
                                        Sex.Male)
parent_1 = node_generator.generate_node(grandparent_1,
                                        grandparent_3,
                                        Sex.Female)



grandchild = node_generator.generate_node(parent_0, parent_1)


### Second configuration, half siblings and more
grandparent_a0 = node_generator.generate_node(sex = Sex.Female)
grandparent_a1 = node_generator.generate_node(sex = Sex.Male)
grandparent_a2 = node_generator.generate_node(sex = Sex.Male)

parent_a0 = node_generator.generate_node(sex = Sex.Female)
parent_a1 = node_generator.generate_node(grandparent_a1,
                                         grandparent_a0,
                                         Sex.Male)
parent_a2 = node_generator.generate_node(grandparent_a2,
                                         grandparent_a0,
                                         Sex.Male)



sibling_0 = node_generator.generate_node(parent_a1, parent_a0)
sibling_1 = node_generator.generate_node(parent_a2, parent_a0)

def generate_genomes(root_nodes, generator, recombinators):
    queue = deque(root_nodes)
    while len(queue) > 0:
        person = queue.popleft()
        if person.mother is not None:
            assert person.father is not None
            person.genome =  mate(person.mother.genome, person.father.genome,
                                  recombinators[Sex.Female],
                                  recombinators[Sex.Male])
        else:
            person.genome = generator.generate()
        queue.extend(person.children)

def clear_genomes(root_nodes):
    pass

recombinators = recombinators_from_directory("../data/recombination_rates")
chrom_sizes = recombinators[Sex.Male]._num_bases
genome_generator = RecombGenomeGenerator(chrom_sizes)


founders_gparent = [great_grandparent_0, great_grandparent_1,
                    great_grandparent_2, grandparent_2, grandparent_3]
founders_siblings = [grandparent_a0, grandparent_a1, grandparent_a2,
                     parent_a0]
sharing_gparent = []
sharing_siblings = []
for i in range(10000):
    generate_genomes(founders_gparent, genome_generator, recombinators)
    generate_genomes(founders_siblings, genome_generator, recombinators)
    shared_gparent = shared_segment_length_genomes(grandchild.genome,
                                                   grandparent_1.genome, 0)
    shared_siblings = shared_segment_length_genomes(sibling_0.genome,
                                                    sibling_1.genome, 0)
    sharing_gparent.append(shared_gparent)
    sharing_siblings.append(shared_siblings)

print(abs(np.mean(sharing_gparent) - np.mean(sharing_siblings)))
print(abs(np.median(sharing_gparent) - np.median(sharing_siblings)))
pdb.set_trace()
