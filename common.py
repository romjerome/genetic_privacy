#!/usr/bin/python
from __future__ import with_statement

from functools import *
from itertools import *

import status, utils, graphing
from pype import *
from pypethread import *

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()

class Node(utils.Struct):
	def __init__(self, id):
		self.id = id
		self.mom = None
		self.dad = None
		self.sex = None
		self.spouses = set()
		self.children = set()

	@property
	def parents(self):
		return (self.dad, self.mom)
	
	@property
	def knownparents(self):
		return ([self.mom] if self.mom else []) + ([self.dad] if self.dad else [])

	def sanityCheck(self):
		for parent in self.knownparents:
			assert self in parent.children
		for child in self.children:
			assert self in child.knownparents

def nearestCommonAncestor(lnode, rnode):
	lfront, rfront = set([lnode]), set([rnode])
	pedigree = set([])

	def extend(nodes):
		return set(utils.flatten(node.knownparents for node in nodes))

	for distance in count(1):
		lfront = extend(lfront)
		rfront = extend(rfront)
		newpedigree = set(pedigree | lfront | rfront)
		if len(newpedigree) < len(pedigree) + len(lfront) | len(rfront):
			return distance
		if not lfront and not rfront:
			return None

def chainOp(node, numsteps, op):
	"""repeat op numsteps times on node"""
	result = [node]
	for spam in xrange(numsteps):
		result = result | Map(op) | pFlatten
	return result

ancestorsByGeneration = partial(chainOp, op=lambda node: node.knownparents)
descendentsByGeneration = partial(chainOp, op=lambda node: node.children)

def cousinsNApart(node, numsteps):
	cousins = ancestorsByGeneration(node, numsteps) |\
				Map(partial(descendentsByGeneration, numsteps=numsteps)) |\
				pFlatten | pSet
	assert len(cousins) == 0 or node in cousins
	return cousins - set([node])

def closureSize(node, op):
	closure = set([node])
	front = set([node])
	while True:
		front = set(utils.flatten(op(node) for node in front))
		if node in front:
			print node
			assert False
		if not (front-closure): #FIXME: find the loop
			return len(closure) - 1
		closure |= front

pedigreeSize = partial(closureSize, op=lambda node: node.knownparents)
progenySize = partial(closureSize, op=lambda node: node.children)


