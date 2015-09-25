from random import sample
from itertools import chain
import pdb

import numpy as np

class SimpleAdversary():
    def __init__(self, population, percent = 0.01, generations = 3):
        self._generations = 3
        self._population = population
        self._individuals = []
        for generation in population.generations[-generations:]:
            new_individuals = sample(generation.members,
                                     int(percent * generation.size))
            self._individuals.extend(new_individuals)

    def identify(self, target):
        kinship = self._population.kinship_coefficients
        target_vector = np.array([kinship[target, person] for person
                                  in self._individuals])
        kinship_error = dict()
        potentials = chain.from_iterable(generation.members for generation
                                         in self._population.generations[-self._generations:])
        for potential in potentials:
            potential_vector = np.array([kinship[potential, person] for person
                                         in self._individuals])
            sqr_error = (target_vector - potential_vector) ** 2
            kinship_error[potential] = np.sum(sqr_error)

        # Return a set because siblings will have the same error.
        return set(person for person, error in kinship_error.items()
                   if error == 0.0)
            
        
        
