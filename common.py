#!/usr/bin/python
from __future__ import with_statement

from functools import *
from itertools import *

import status, utils #, graphing
from pype import *
from pypethread import *

data_dir = 'data'

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()

class Node(utils.Struct):
	
	__slots__ = 'location generation sex mom dad children ispublic isalive'.split()

	def __init__(self, id):
		self.id = id
		self.mom = None
		self.dad = None
		self.sex = None
		#self.spouses = set()
		self.children = set()

	@property
	def parents(self):
		return (self.dad, self.mom)
	
	@property
	def siblings(self):
		return self.dad.children & self.mom.children
	
	@property
	def knownparents(self):
		return ([self.mom] if self.mom else []) + ([self.dad] if self.dad else [])

def sanityCheck(node):
	for parent in node.knownparents:
		assert node in parent.children
	for child in node.children:
		assert node in child.knownparents

@utils.cached()
def relationMap(node, height=8, depth=8, maxdist=13):
	"""FIXME: debug this thoroughly"""
	front = set([node])
	relmap = {node: {(0,0):1}}

	def climb(dir, front, relmap, height, seen=set()):
		nbrs = lambda n: set(n.knownparents) if dir == "up" else n.children
		for spam in xrange(height):
			for f in front:
				for (h_up, h_down), cnt in relmap.get(f, {}).iteritems():
					if h_up + h_down >= maxdist:
						continue
					for p in nbrs(f) - seen:
						key = (h_up+1, h_down) if dir == "up" else (h_up, h_down+1)
						dic = relmap.setdefault(p, {})
						dic[key] = dic.get(key, 0) + cnt
			seen |= front
			front = (map(nbrs, front) | pFlatten | pSet) - seen
		return front
	front = climb("up", front, relmap, height)
	seen = set(relmap)
	climb("down", front | seen, relmap, depth, seen)

	for n in relmap.keys():
		if not n.isalive:
			del relmap[n]
	return relmap

def nearestCommonAncestor(lnode, rnode):
	lfront, rfront = set([lnode]), set([rnode])
	pedigree = set([])

	def extend(nodes):
		return set(utils.flatten(node.knownparents for node in nodes))

	for distance in count(1):
		lfront = extend(lfront)
		rfront = extend(rfront)
		newpedigree = set(pedigree | lfront | rfront)
		if len(newpedigree) < len(pedigree) + len(lfront) + len(rfront):
			return distance
		if not lfront and not rfront:
			return None
		pedigree = newpedigree

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
		if not (front-closure): #FIXME: find the loops in the LDS data
			return len(closure) - 1
		closure |= front

pedigreeSize = partial(closureSize, op=lambda node: node.knownparents)
progenySize = partial(closureSize, op=lambda node: node.children)


#size=100000
#nodes=[[mate.Node(None, None) for spam in xrange(size)]]
#for i in xrange(size): nodes[0][i].location = i
#for gen in xrange(1,10):
#	newgen=mate.newGen(nodes[-1],size)
#	mate.postProcessLocation(newgen)
#	nodes.append(newgen)
#c5e = lambda n: c5(n) - c4(n)
#c5 = partial(common.cousinsNApart, numsteps=5)
#c4 = partial(common.cousinsNApart, numsteps=4)
#nca = common.nearestCommonAncestor
##map(lambda n:map(lambda m:nca(n,m),reduce(operator.__and__, map(c5, utils.sampleWoR(c5(n)|pList, 5)))), utils.sampleWoR(nodes[9], 2))
#map(lambda n:len(reduce(operator.__and__, map(c5e, utils.sampleWoR(c5e(n)|pList, 6))))-len(n.dad.children), utils.sampleWoR(nodes[9], 20))
