#!/usr/bin/env python3

import pdb

from model import Generation, Population, generate_population
from adversary import SimpleAdversary

print("Generating population")
population = generate_population(1000)

print("Creating 10 generations.")
for _ in range(10):
    population.new_generation()
    
print("Creating adversary.")
adversary = SimpleAdversary(population)

last_generation = population.generations[-1]
person = last_generation.members[-1]

print("Identifying person.")
identified_as = adversary.identify(person)
print(identified_as is person)

pdb.set_trace()
