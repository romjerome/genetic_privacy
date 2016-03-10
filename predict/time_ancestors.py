#!/usr/bin/env python3

from pickle import load
from timeit import timeit, repeat
from itertools import chain

with open("ancestors_of_timing.pickle", "rb") as pickle_file:
    population = load(pickle_file)

nodes = population.generations[-1].members

TRIALS = 50

def immediate_ancestors_of_1(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    ancestors = set()
    for node in nodes:
        if node is None:
            continue
        ancestors.add(node.mother)
        ancestors.add(node.father)
    ancestors.discard(None)
    return ancestors

def immediate_ancestors_of_2(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    mothers = [node.mother for node in nodes]
    fathers = [node.father for node in nodes]
    ancestors = set(chain(mothers, fathers))
    ancestors.discard(None)
    return ancestors

def immediate_ancestors_of_3(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    mothers = [node.mother for node in nodes]
    fathers = [node.father for node in nodes]
    ancestors = set(mothers)
    ancestors.update(fathers)
    ancestors.discard(None)
    return ancestors

def immediate_ancestors_of_4(nodes):
    """
    Given an iterable of nodes, returns set of nodes containing the
    parents of nodes in nodes.
    """
    pairs = [(node.mother, node.father) for node in nodes]
    ancestors = set(chain.from_iterable(pairs))
    ancestors.discard(None)
    return ancestors

method_1_time = min(repeat(lambda: immediate_ancestors_of_1(nodes), number = TRIALS))
print("Min method 1 time {}".format(method_1_time / TRIALS))

method_2_time = min(repeat(lambda: immediate_ancestors_of_2(nodes), number = TRIALS))
print("Min method 2 time {}".format(method_2_time / TRIALS))

method_3_time = min(repeat(lambda: immediate_ancestors_of_3(nodes), number = TRIALS))
print("Min method 3 time {}".format(method_3_time / TRIALS))

method_4_time = min(repeat(lambda: immediate_ancestors_of_4(nodes), number = TRIALS))
print("Min method 4 time {}".format(method_4_time / TRIALS))


