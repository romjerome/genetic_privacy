#!/usr/bin/env python3

from model import Generation, Population, generate_population

print("Generating population")
population = generate_population(1000)

print("Creating 10 generations.")
for _ in range(10):
    population.new_generation()
    
for i, generation in enumerate(population._generations):
    if i is 0:
        continue
    previous_generation_members = set(population._generations[i-1].members)
    for member in generation.members:
        assert member.mom in previous_generation_members
        assert member.dad in previous_generation_members
