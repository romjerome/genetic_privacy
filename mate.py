#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random

from functools import *
from itertools import *

import status, utils, smartcache, graphing
from pype import *
from pypethread import *

import common

MALE, FEMALE = "male", "female"

num_children_distribution = [17.9, 17.4, 35.4, 18.9, 6.8, 1.8, 1.0, 0.8]

class Node:
	pass

def makePairsRandom(males, females):
	numpairs = min(len(males), len(females))
	return zip(utils.permute(males)[:numpairs], utils.permute(females)[:numpairs])


def newGen(oldgen, size):
	"""generate children for each mating pair independently
	then add or remove according to same distribution until you hit required size"""
	males = [n for n in oldgen if n.sex == MALE]
	females = [n for n in oldgen if n.sex == FEMALE]
	pairs = makePairsRandom(males, females)
	newgen = []
	for dad, mom in pairs:
		newgen.extend(makeChildren(dad, mom))
	while len(newgen) < size:
		randomchild = random.choice(newgen)
		newgen.append(Node(randomchild.dad, randomchild.mom))
	return newgen
	

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
