#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, itertools, os

from functools import *
from itertools import *

import status, utils, graphing
from pype import *

MALE, FEMALE = 0, 1

def parseGED(filename):
	with open(filename) as f:
		curblock = []
		inblock = False
		for line in f:
			if line.startswith('0') and len(curblock) > 0:
				yield curblock
				curblock = []
				inblock = False
			if re.search('0.*FAM', line):
				inblock = True
			if inblock:
				match = re.match('1 (HUSB|WIFE|CHIL) @(....*)@', line)
				if match:
					nodetype, nodeid = match.groups()
					curblock.append((nodetype, nodeid))

class Node(utils.Struct):
	def __init__(self, id):
		self.id = id
		self.mom = None
		self.dad = None
		self.sex = None
		self.spouses = set()
		self.children = set()

	def knownParents(self):
		return ([self.mom] if self.mom else []) + ([self.dad] if self.dad else [])

def sanityCheck(node):
	for parent in node.knownParents():
		assert node in parent.children
	for child in node.children:
		assert node in child.knownParents()

_allnodes = {}

def getNode(id):
	global _allnodes
	return _allnodes.setdefault(id, Node(id))

def processBlock(block):
	children = []
	dad, mom = None, None
	for nodetype, nodeid in block:
		if nodetype == 'HUSB':
			dad = getNode(nodeid)
			assert dad.sex in (MALE, None)
			dad.sex = MALE
		if nodetype == 'WIFE':
			mom = getNode(nodeid)
			assert mom.sex in (FEMALE, None)
			mom.sex = FEMALE
		if nodetype == 'CHIL':
			children.append(getNode(nodeid))

	if dad and mom:
		dad.spouses.add(mom)
		mom.spouses.add(dad)

	for child in children:
		if child.dad or child.mom: #this ensures parents are always spouses
			continue
		if dad:
			dad.children.add(child)
			child.dad = dad
		if mom:
			mom.children.add(child)
			assert child.mom in (mom, None)
			child.mom = mom


def nearestCommonAncestor(lnode, rnode):
	lfront, rfront = set([lnode]), set([rnode])
	pedigree = set([])

	def extend(nodes):
		return set(utils.flatten(node.knownParents() for node in nodes))

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

ancestorsByGeneration = partial(chainOp, op=lambda node: node.knownParents())
descendentsByGeneration = partial(chainOp, op=lambda node: node.children)

def cousinsNApart(node, numsteps):
	cousins = ancestorsByGeneration(node, numsteps) | Map(partial(descendentsByGeneration, numsteps=numsteps)) | pFlatten | pSet
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

pedigreeSize = partial(closureSize, op=lambda node: node.knownParents())
progenySize = partial(closureSize, op=lambda node: node.children)

def readData():
	gedfiles = os.popen('ls data | grep family') | pStrip | pList
	for filename in gedfiles:
		map(processBlock, parseGED('data/' + filename))
		status.status(total=len(gedfiles))

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
