from __future__ import with_statement

"""
	evolves diploid genomes given family tree
"""
import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy

from functools import *
from itertools import *

import status, utils
from pype import *

from chrlen import chromelengths

#TOP, BOT = 0, 1

class Chromosome:
	def __init__(self, number, top=None, bot=None):
		self.number = number
		length = chromelengths[number]
		def randomChrome(size):
			return array.array('B', [random.randrange(256) for spam in xrange(size)])
		self.top = top if top else randomChrome(length/8)
		self.bot = bot if bot else randomChrome(length/8)

def crossOver(topseg, botseg):
	length = chromelengths[number]
	chiasmas = []
	cur_chiasma = 0
	topseg, botseg = utils.permute(topseg, botseg)
	while True:
		cur_chiasma += int(morgan * (-math.log(random.random())))
		if cur_chiasma >= length:
			break
		chiasmas.append(cur_chiasma)
	if not chiasmas:
		return topseg
	outseg = []
	for (which, left, right) in topseg:
		if even number of recombinations: # TODO
			outseg.append((which, left, right))
		if need to split:
			#TODO
	for (which, left, right) in botseg:
		if odd number of recombinations:
			outseg.append((which, left, right))
		if need to split:
			#TODO
	return outseg


class Node:
	"""a node in the family tree"""
	def mate(self, lparent, rparent):
		for chrnum in xrange(1, 23):
			self.segments[chrnum][TOP], self.segments[chrnum][BOT] = utils.permute(
				crossOver(chrnum, lparent.segments[chrnum]),
				crossOver(chrnum, rparent.segments[chrnum])
			)
			
