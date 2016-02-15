#!/usr/bin/env python3.5

from pickle import load
from classify_relationship import LengthClassifier, common_ancestor_vector

with open("population_40000.pickle", "rb") as pickle_file:
    population = load(pickle_file)

classifier = LengthClassifier(population, 200)

