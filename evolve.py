from __future__ import with_statement

"""
	evolves diploid genomes given family tree
"""
import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy, array, copy, numpy

from functools import *
from itertools import *

import status, utils
from pype import *

from chrlen import chromelengths, sniplengths

TOP, BOT = 0, 1

defaultchromes = dict((chrnum, numpy.array([random.randrange(256) for spam in xrange(sniplengths[chrnum]/8)], numpy.uint8)) for chrnum in xrange(1, 23))

class Chromosome:
	def __init__(self, number, top=None, bot=None):
		self.number = number
		length = sniplengths[number]
		def randomChrome(size):
			return copy.deepcopy(defaultchromes[number])
		self.top = top if top is not None else randomChrome(length/8)
		self.bot = bot if bot is not None else randomChrome(length/8)


def segments2Chrome(chrnum, segments):
	return numpy.concatenate([ances[left/2800/8:right/2800/8] for (ances, left, right) in sorted(segments, key = lambda (ances, left, right): left)])

def crossOver(chrnum, topsegs, botsegs):
	"""given two sets of segments corresponding to two homologous chromosomes, 
	produce segments for result of crossover"""
	length = chromelengths[chrnum]
	morgan = 1e8
	topsegs, botsegs = utils.permute([topsegs, botsegs])

	cur_chiasma = 0
	chiasmas = []
	while True:
		cur_chiasma += int(morgan * (-math.log(random.random())))
		if cur_chiasma >= length:
			break
		chiasmas.append(cur_chiasma)
	chiasmas.append(length) # one fake chiasma

	if len(chiasmas) == 1:
		return topsegs
			
	outsegs = []
	insegs = [tup + (0,) for tup in topsegs] + [tup + (1,) for tup in botsegs] 
	for (which, left, right, parity) in insegs:
		for idx in xrange(parity, len(chiasmas), 2):
			chi = chiasmas[idx]
			if chi < left:
				continue
			prevchi = chiasmas[idx-1] if idx > 0 else 0
			if right < prevchi:
				break
			outsegs.append((which, max(left, prevchi), min(right, chi)))

	return outsegs

class Node:
	"""a node in the family tree"""
	def mate(self):
		"""produce segments based on crossing over parents'"""
		for chrnum in xrange(1, 23):
			self.segments[chrnum] = utils.permute((
				crossOver(chrnum, *self.lparent.segments[chrnum]),
				crossOver(chrnum, *self.rparent.segments[chrnum])
			))
			
	def initSegments(self):
		self.segments = dict((chrnum, 
						([(self.chromosomes[chrnum].top, 0, chromelengths[chrnum])], 
						 [(self.chromosomes[chrnum].bot, 0, chromelengths[chrnum])]))
						for chrnum in xrange(1, 23))

	def copyChromes(self):
		for chrnum in xrange(1, 23):
			self.chromosomes[chrnum] = Chromosome(chrnum, 
										segments2Chrome(chrnum, self.segments[chrnum][0]),
										segments2Chrome(chrnum, self.segments[chrnum][1])
										)
		self.initSegments()

	def __init__(self, id, lparent=None, rparent=None):
		"""if we have no parents, we are a root, 
		so segments are initialized accordingly"""
		self.id = id
		self.lparent = lparent
		self.rparent = rparent
		if self.lparent:
			self.segments = {}
			self.mate()
			self.chromosomes = {}
		else:
			self.chromosomes = dict((chrnum, Chromosome(chrnum)) for chrnum in xrange(1,23))
			self.initSegments()

def evolve(numgens=10, popsize=1000, batchsize=10):
	nodes = {}
	nodes[0] = [Node(i) for i in xrange(popsize)]
	for gen in xrange(1, numgens+1):
		sys.stderr.write("generation %d\n" % gen)
		nodes[gen] = [Node(i, *utils.sampleWoR(nodes[gen-1], 2)) for i in xrange(popsize)]
		if gen % batchsize == 0:
			for node in nodes[gen]:
				node.copyChromes()
		
#n1, n2 = evolve.Node(1), evolve.Node(2); n3 = evolve.Node(3, n1, n2); n3.mate()
#n3.segments
