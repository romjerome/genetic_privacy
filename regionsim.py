from __future__ import with_statement
# test self-correlation and cross-correlation between people

import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy

from functools import *
from itertools import *

import status, utils
from pype import *

def childRegion((lchrome, rchrome)):
	def flipIfNeeded((x, y)):
		return (x, y) if x <= y else (y, x)

	def intersect((x1, y1), (x2, y2)):
		return (max(x1, x2), min(y1, y2))
	
	lcross = flipIfNeeded((random.choice((0.0, 1.0)), random.random()))
	rcross = flipIfNeeded((random.choice((0.0, 1.0)), random.random()))

	return intersect(lchrome, lcross), intersect(rchrome, rcross)

def descendentRegion(chrome, numgen):
	for spam in xrange(numgen):
		chrome = childRegion(chrome)
	return chrome

def descendentLength(chrome, numgen):
	lchrome, rchrome = descendentRegion(chrome, numgen)
	def regionProb((x, y)):
		return max(y-x, 0)
	return max(regionProb(lchrome), regionProb(rchrome))

def makePlot(sampleThunk, chromelengths, bucketlen=1000, numsamples=10000):
	samples = [max(int(sampleThunk()*cl/bucketlen) * bucketlen for cl in chromelengths) \
					for spam in xrange(numsamples)]
	hist = utils.getHist(samples)
	return 	[bucketlen * x for x in xrange(max(chromelengths) / bucketlen)],\
			[hist.get(bucketlen * x, 0) for x in xrange(max(chromelengths) / bucketlen)]

def readChromeLengths(filename="data/chrlen", numsnips=1e6):
	with open(filename) as file:
		bpcounts = file | Map(int) | pList
	snipcounts = [int(n * 1e6 / sum(bpcounts)) for n in bpcounts]
	return snipcounts


#top = ((0,1),(0,1))
#regionsim.makePlot(partial(regionsim.descendentLength, chrome=top, numgen=3))
