#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, cProfile

from functools import *
from itertools import *

import status, utils #, graphing
from pype import *
from pypethread import *

import common

MALE, FEMALE = "male", "female"

num_children_distribution = [17.9, 17.4, 35.4, 18.9, 6.8, 1.8, 1.0, 0.8]

class Node(common.Node):
	def __init__(self, dad, mom, sex=None):
		self.dad = dad
		self.mom = mom
		self.sex = sex or random.choice((MALE, FEMALE))
		self.children = set()
		self.spouses = set()

def splitSexes(nodes):
	males = [n for n in nodes if n.sex == MALE]
	females = [n for n in nodes if n.sex == FEMALE]
	return males, females

def makePairsRandom(nodes):
	males, females = splitSexes(nodes)
	numpairs = min(len(males), len(females))
	return zip(utils.permute(males)[:numpairs], utils.permute(females)[:numpairs])

def makePairs1D(nodes, meandist=100, matingfraction=0.9):
	"""generate mating pairs from nodes
	affinity for nearby nodes (topology is a ring) with mean dist meandist
	only matingfraction of nodes mate"""
	loc2node = ((node.location, node) for node in nodes) | pDict
	assert sorted(loc2node.keys()) == range(len(nodes))
	assert 2 * min(map(len, splitSexes(nodes))) >= len(nodes) * matingfraction
	mated = set()
	while len(mated) < matingfraction * len(nodes):
		while True:
			#node = list(utils.sampleWoR(nodes, 1))[0]
			node = random.choice(nodes)
			if node not in mated:
				break
		matedist = int(math.log(1/random.random()) * meandist + 0.5)
		def matesByOffset(offset):
			newlocs = (node.location + matedist + offset,
						node.location + matedist - offset,
						node.location - matedist + offset,
						node.location - matedist - offset)
			return [loc2node[loc % len(nodes)] for loc in newlocs]
		mate = xrange(len(nodes)) | Map(matesByOffset) | pFlatten |\
			Filter(lambda m: m.sex != node.sex and m not in mated) | pFirst
		mated.add(node)
		mated.add(mate)
		dad, mom = (node, mate) if node.sex == MALE else (mate, node)
		yield dad, mom

def makeChildren((dad, mom)):
	sampler = utils.getattrdefault(makeChildren, 'sampler',
							lambda: utils.Sampler(range(len(num_children_distribution)),
									num_children_distribution.__getitem__))
	numchildren = sampler.sample()
	children = [Node(dad, mom) for spam in xrange(numchildren)]
	if hasattr(dad, 'generation') and hasattr(mom, 'generation')\
							and dad.generation == mom.generation:
		generation = dad.generation + 1
	else:
		generation = None
	for child in children:
		dad.children.add(child)
		mom.children.add(child)
		if generation is not None:
			child.generation = generation
	return children

def newGen(oldgen, size):
	"""generate children for each mating pair independently
	then add or remove according to same distribution until you hit required size"""
	newgen = makePairs1D(oldgen) | Map(makeChildren) | pFlatten | pList
	while len(newgen) < size:
		randomchild = random.choice(newgen)
		newchild = Node(randomchild.dad, randomchild.mom)
		randomchild.dad.children.add(newchild)
		randomchild.mom.children.add(newchild)
		newgen.append(newchild)
	return newgen

def postProcessLocation(nodes):
	"""sets locations for nodes.  NOTE: destructive"""
	def sortKey(n):
		oldlocs = (n.dad.location, n.mom.location)
		newloc = sum(oldlocs) / 2.0 + 0.5 * random.random()
		if max(oldlocs) - min(oldlocs) > len(nodes) / 2:
			newloc += len(nodes) / 2
			newloc %= len(nodes)
		return newloc
	for node, idx in izip(sorted(nodes, key=sortKey), count()):
		node.location = idx

def makeTree(size=100000, generations=10):
	nodes=[[Node(None, None) for spam in xrange(size)]]
	for i in xrange(size):
		nodes[0][i].location = i
		nodes[0][i].generation = 0
	for gen in xrange(1,generations):
		newgen = newGen(nodes[-1],size)
		postProcessLocation(newgen)
		nodes.append(newgen)
		status.status(total=generations-1)
	return nodes

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()
	cProfile.run("makeTree(20000,2)")

if __name__ == "__main__": main()
