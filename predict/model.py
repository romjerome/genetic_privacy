from generation import Generation
from population import Population
from node import Node


def generate_population(size):
    initial_generation = Generation(Node() for _ in range(size))
    return Population(initial_generation)

class PopulationGenerator():
    pass


class HIMPopulationGeneration(PopulationGenerator):
    """
    Generate a population based on the a hierarchical island model.
    """
    def __init__(self, num_islands)
