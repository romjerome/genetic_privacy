#!/usr/bin/env python3

from random import sample, choice

from bayes_deanonymize import BayesDeanonymize
from population import PopulationUnpickler

NUM_LABELED = 10

with open("population_40000.pickle", "rb") as pickle_file:
    population = PopulationUnpickler(pickle_file).load()


last_generation = population.generations[-1].members
labeled_nodes = set(sample(last_generation, NUM_LABELED))

bayes = BayesDeanonymize(population, labeled_nodes)

# unlabeled = sample(list(set(last_generation) - labeled_nodes), 2)
unlabeled = [choice(list(set(last_generation) - labeled_nodes))]
correct = 0
incorrect = 0
for node in unlabeled:
    if bayes.identify(node.genome) == node:
        correct += 1
    else:
        incorrect += 1


print("{} correct, {} incorrect, {} total.".format(correct, incorrect,
                                                  len(unlabeled)))
print("{} percent accurate.".format(correct / len(unlabeled)))
