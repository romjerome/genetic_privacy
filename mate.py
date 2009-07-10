#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random

from functools import *
from itertools import *

import status, utils, graphing
from pype import *
from pypethread import *

import common

MALE, FEMALE = "male", "female"

num_children_distribution = [17.9, 17.4, 35.4, 18.9, 6.8, 1.8, 1.0, 0.8]

class Node(common.Node):
	def __init__(self, dad, mom, sex=None):
		self.dad = dad
		self.mom = mom
		self.sex = random.choice((MALE, FEMALE)) if sex is None else sex
		self.children = set()
		self.spouses = set()

def makePairsRandom(males, females):
	numpairs = min(len(males), len(females))
	return zip(utils.permute(males)[:numpairs], utils.permute(females)[:numpairs])

def makeChildren((dad, mom)):
	numchildren = utils.Sampler(range(len(num_children_distribution)),
								num_children_distribution.__getitem__).sample()
	children = [Node(dad, mom) for spam in xrange(numchildren)]
	for child in children:
		dad.children.add(child)
		mom.children.add(child)
	return children

def newGen(oldgen, size):
	"""generate children for each mating pair independently
	then add or remove according to same distribution until you hit required size"""
	males = [n for n in oldgen if n.sex == MALE]
	females = [n for n in oldgen if n.sex == FEMALE]
	pairs = makePairsRandom(males, females)
	newgen = pairs | Map(makeChildren) | pFlatten | pList
	while len(newgen) < size:
		randomchild = random.choice(newgen)
		newgen.append(Node(randomchild.dad, randomchild.mom))
	return newgen

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
