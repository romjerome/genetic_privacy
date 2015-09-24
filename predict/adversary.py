from random import sample
import pdb

import numpy as np

class SimpleAdversary():
    def __init__(self, population, percent = 0.01, generations = 3):
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
        for potential in self._population.members:
            potential_vector = np.array([kinship[potential, person] for person
                                         in self._individuals])
            if potential is target:
                pdb.set_trace()
            sqr_error = (target_vector - potential_vector) ** 2
            kinship_error[potential] = np.sum(sqr_error)

        return min((item[1], item[0]) for item in kinship_error.items())[1]
            
        
        
