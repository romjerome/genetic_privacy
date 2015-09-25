#!/usr/bin/env python3

import pdb

from progressbar import ProgressBar

from model import generate_population
from adversary import SimpleAdversary


print("Generating population")
population = generate_population(1000)

print("Creating 9 new generations.")
for _ in range(9):
    population.new_generation()
    
print("Creating adversary.")
adversary = SimpleAdversary(population, 0.001, 1)

last_generation = population.generations[-1]

print("Identifying individuals.")
progress = ProgressBar()
correct_guesses = 0
incorrect_guesses = 0
for person in progress(last_generation.members):
    if person in adversary.identify(person):
        correct_guesses += 1
    else:
        incorrect_guesses += 1

output_string = "Total guesses: {}, correct_guesses: {}, incorrect_guesses: {}"
print(output_string.format(correct_guesses + incorrect_guesses,
                           correct_guesses, incorrect_guesses))
accuracy = correct_guesses / (correct_guesses + incorrect_guesses)
print("Accuracy: {}".format(accuracy))
pdb.set_trace()
