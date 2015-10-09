from generation import Generation
from population import Population
from node import Node


def generate_population(size):
    initial_generation = Generation(Node() for _ in range(size))
    return Population(initial_generation)

