#!/usr/bin/env python3

from model import generate_population
from generation import Generation
from population import Population
from node import Node
from sex import Sex

ERROR_STRING = "Expected kinship to be {}, was {}."

population = Population()

maternal_greatgrandfather = Node(sex = Sex.Male)
maternal_greatgrandmother = Node(sex = Sex.Female)

greatgrandparent_generation = Generation([maternal_greatgrandfather,
                                          maternal_greatgrandmother])

maternal_grandfather = Node(maternal_greatgrandfather,
                            maternal_greatgrandmother, sex = Sex.Male)
paternal_grandfather = Node(sex = Sex.Male)
maternal_grandmother = Node(sex = Sex.Female)
paternal_grandmother = Node(sex = Sex.Female)

maternal_grandfather_brother = Node(maternal_greatgrandfather,
                                    maternal_greatgrandmother, sex = Sex.Male)
maternal_grandfather_brother_mate = Node(sex = Sex.Female)

grandparent_generation = Generation([maternal_grandfather, paternal_grandfather,
                                     maternal_grandmother, paternal_grandmother,
                                     maternal_grandfather_brother,
                                     maternal_grandfather_brother_mate])

mother = Node(maternal_grandfather, maternal_grandmother, sex = Sex.Female)
maternal_uncle = Node(maternal_grandfather, maternal_grandmother,
                      sex = Sex.Male)
maternal_uncle_mate = Node(sex = Sex.Female)
maternal_grandfather_brother_son = Node(maternal_grandfather_brother,
                                        maternal_grandfather_brother_mate,
                                        sex = Sex.Male)
maternal_grandfather_brother_son_mate = Node(sex = Sex.Female)

father = Node(paternal_grandfather, paternal_grandmother, sex = Sex.Male)
parent_generation = Generation([mother, father, maternal_uncle,
                                maternal_uncle_mate,
                                maternal_grandfather_brother_son,
                                maternal_grandfather_brother_son_mate])

child = Node(father, mother)
cousin = Node(maternal_uncle, maternal_uncle_mate)
second_cousin = Node(maternal_grandfather_brother_son,
                     maternal_grandfather_brother_son_mate)
current_generation = Generation([child, cousin, second_cousin])
population._generations = [greatgrandparent_generation, grandparent_generation,
                           parent_generation, current_generation]

kinship = population.kinship_coefficients


def test_kinship(person_1, person_2, expected):
    key = (person_1, person_2)
    assert kinship[key] == expected, ERROR_STRING.format(expected, kinship[key])

test_kinship(child, mother, 0.25)
test_kinship(child, father, 0.25)
test_kinship(child, maternal_grandfather, 1/8)
test_kinship(child, paternal_grandfather, 1/8)
test_kinship(child, maternal_grandmother, 1/8)
test_kinship(child, paternal_grandmother, 1/8)
test_kinship(child, maternal_uncle, 1/8)
test_kinship(child, cousin, 1/16)
test_kinship(child, second_cousin, 1/64)


