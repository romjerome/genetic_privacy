from __future__ import with_statement
# test self-correlation and cross-correlation between people

import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy

from functools import *
from itertools import *

import status, utils
from pype import *

from chrlen import chromelengths

TOP, BOT = 0, 1

class Chromosome:
	def __init__(self, number, top=None, bot=None):
		self.number = number
		self.top = top if top is not None else [(TOP, 0, chromelengths[number])]
		self.bot = bot if bot is not None else [(BOT, 0, chromelengths[number])]

	def __str__(self):
		return "top: %s\nbot: %s" % (self.top, self.bot)

def childChrome(chrome):
	def flipIfNeeded((x, y)):
		return (x, y) if x <= y else (y, x)

	def intersect((x1, y1), (x2, y2)):
		return (max(x1, x2), min(y1, y2))

	strands = [chrome.top, chrome.top, chrome.bot, chrome.bot]
	locus = 0
	crossoverfreq = 5e7
	while True:
		locus += int(crossoverfreq * (-math.log(random.random())))
		if locus >= chromelengths[chrome.number]:
			break
		str_id1, str_id2 = utils.sampleWoR(range(4), 2)
		topstrand, botstrand = [], []

		#TODO: off by one issues
		def halfCrossover(fromstrand, tostrand1, tostrand2, locus):
			for which, left, right in fromstrand:
				if right <= locus:
					tostrand1.append((which, left, right))
				elif left > locus:
					tostrand2.append((which, left, right))
				else:
					tostrand1.append((which, left, locus))
					tostrand2.append((which, locus+1, right))
		halfCrossover(strands[str_id1], topstrand, botstrand, locus)
		halfCrossover(strands[str_id2], botstrand, topstrand, locus)
		strands[str_id1], strands[str_id2] = topstrand, botstrand

	return Chromosome(chrome.number, random.choice(strands), [])
	
#TODO:
# * cousins

@utils.materialize
def intersectStrands(lstrand, rstrand):
	for lwhich, lleft, lright in lstrand:
		for rwhich, rleft, rright in rstrand:
			if lwhich != rwhich:
				continue
			if rright < lleft or lright < rleft:
				continue
			yield (lwhich, max(lleft, rleft), min(lright, rright))

def cousinLength(chrnum, lnumgen, rnumgen):
	lstrand = descendentChrome(Chromosome(chrnum), lnumgen).top
	rstrand = descendentChrome(Chromosome(chrnum), rnumgen).top
	return maxLength(intersectStrands(lstrand, rstrand))

def descendentChrome(chrome, numgen):
	for spam in xrange(numgen):
		chrome = childChrome(chrome)
	return chrome

def maxLength(strand):
	basepairspersnip = 3000
	lengths = map(lambda (w, l, r): r-l, strand)
	return max([0] + lengths) / basepairspersnip

def descendentLength(chrnum, numgen):
	return maxLength(descendentChrome(Chromosome(chrnum), numgen).top)

def makePlot(sampleThunk, bucketlen=1000, numsamples=10000):
	chromesamples = [[sampleThunk(chrnum) for spam in xrange(numsamples/10)] \
					for chrnum in xrange(1, 23)]
	samples = [max(random.choice(cs) for cs in chromesamples) \
				for spam in xrange(numsamples)]
	hist = utils.getHist([int(x+bucketlen/2)/bucketlen * bucketlen for x in samples])
	return 	[bucketlen * x for x in xrange(max(samples) / bucketlen)],\
			[float(hist.get(bucketlen * x, 0)) / numsamples \
					for x in xrange(max(samples) / bucketlen)]

def readChromeLengths(filename="data/chrlen", numsnips=1e6):
	with open(filename) as file:
		bpcounts = file | Map(int) | pList
	snipcounts = [int(n * 1e6 / sum(bpcounts)) for n in bpcounts]
	return snipcounts


#top = ((0,1),(0,1))
#regionsim.makePlot(partial(regionsim.descendentLength, chrome=top, numgen=3))
#pylab.plot(*regionsim.makePlot(partial(regionsim.cousinLength, lnumgen=5, rnumgen=5)))

