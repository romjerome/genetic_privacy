#!/usr/bin/env python3

from pickle import load
from random import sample, choice

from bayes_deanonymize import BayesDeanonymize

NUM_LABELED = 1000

with open("population_40000.pickle", "rb") as pickle_file:
    population = load(pickle_file)


last_generation = population.generations[-1].members
labeled_nodes = set(sample(last_generation, NUM_LABELED))

bayes = BayesDeanonymize(population, labeled_nodes)

# unlabeled = sample(list(set(last_generation) - labeled_nodes), 10)
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
