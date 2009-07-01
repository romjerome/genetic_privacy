#!/usr/bin/python

import sys, re, operator, math, string, os.path, hashlib, random, itertools

from functools import *
from itertools import *

import status, utils
from pype import *

MALE, FEMALE = 0, 1

def parseGed(filename):
	with open(filename) as f:
		curblock = []
		for line in f:
			match = re.match('1 ([A-Z]{4}) @(.*)@', line)
			if match:
				nodetype, nodeid = match.groups()
				assert nodetype in 'HUSB WIFE CHIL'.split()
				curblock.append((nodetype, nodeid))
			else:
				if len(curblock) > 0:
					yield curblock

class Node:
	def __init__(self, id):
		self.id = id
		self.sex = None
		self.spouse = None

_allnodes = {}

def getNode(id):
	global _allnodes
	return _allnodes.setdefault(id, Node(id))

def processBlock(block):
	children = []
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

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
