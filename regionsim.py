from __future__ import with_statement

"""computes expected characteristics (e.g, max. length) of 
shared contiguous regions across simulated meiosis for arbitrarily related humans"""

import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy

from scipy import integrate

from functools import *
from itertools import *

import status, utils
from pype import *

from chrlen import chromelengths, geneticlengths

TOP, BOT = 0, 1

def gammaDensity(x, nu=4.3):
	return math.exp(-2*nu*x) * (2*nu)**nu * x**(nu-1) /  8.85

def pdfSample(f, interval, epsilon=1e-6):
	unisample = random.random()
	xmin, xmax = map(float, interval)
	f_int = lambda x: integrate.quad(f, interval[0], x)[0]
	inttable = {}
	get_int = lambda x: inttable.setdefault(x, f_int(x))
	while xmax - xmin > epsilon:
		xmid = (xmax + xmin) / 2
		if integrate.quad(f, interval[0], xmid)[0] > unisample:
			xmax = xmid
		else:
			xmin = xmid
	return (xmax + xmin) / 2

#gammaSample = partial(pdfSample, f=gammaDensity, interval=(0, 10)) #10 is infinity
def gammaSample():
	try:
		samples = gammaSample._samples
	except:
		samples = gammaSample._samples = []
	if len(samples) < 10000:
		samples.append(pdfSample(gammaDensity, (0, 10)))
		return samples[-1]
	return random.choice(samples)

def recombLoci(geneticlength):
	x = random.random() * gammaSample() #initial chiasma, stationarity condition
	while True:
		if x > geneticlength:
			raise StopIteration
		if random.randrange(2) == 0: #thinning (xover vs recombination)
			yield x
		x += gammaSample()


class Chromosome:
	""" a chromosome pair, made of homologous chromosomes top and bot
		each consists of a list of triples (which, left, right) that track the 
		material derived from a specific ancestor. which = TOP or BOTTOM
		and (left, right) is the region on the chromosome
	"""
	def __init__(self, number, top=None, bot=None):
		self.number = number
		self.top = top if top is not None else [(TOP, 0, geneticlengths[number])]
		self.bot = bot if bot is not None else [(BOT, 0, geneticlengths[number])]

	def __str__(self):
		return "top: %s\nbot: %s" % (self.top, self.bot)

def childChrome(chrome):
	""" assuming uniform, non-interfering crossover on genetic lengths
		chromosome from specified parent is always top
	"""
	top, bot = chrome.top, chrome.bot
	for locus in recombLoci(geneticlengths[chrome.number]):
		newtop, newbot = [], []

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
		halfCrossover(top, newtop, newbot, locus)
		halfCrossover(bot, newbot, newtop, locus)
		top, bot = newtop, newbot

	return Chromosome(chrome.number, random.choice([top, bot]), [])
	
@utils.materialize
def intersectStrands(lstrand, rstrand):
	for lwhich, lleft, lright in lstrand:
		for rwhich, rleft, rright in rstrand:
			if lwhich != rwhich:
				continue
			if rright < lleft or lright < rleft:
				continue
			yield (lwhich, max(lleft, rleft), min(lright, rright))

def maxLength(strand):
	basepairspersnip = 3000
	lengths = map(lambda (w, l, r): r-l, strand)
	return max([0] + lengths) / basepairspersnip

def halfcousinLength(chrnum, lnumgen, rnumgen):
	"""	expected max. length of shared material in half-cousins with a single common
		ancestor lnumgen and rnumgen generations above, respectively"""
	lstrand = descendentChrome(Chromosome(chrnum), lnumgen).top
	rstrand = descendentChrome(Chromosome(chrnum), rnumgen).top
	return maxLength(intersectStrands(lstrand, rstrand))

def relativeLength(chrnum, ancestors):
	"""	expected max. length of shared material in relatives who share a list
		of ancestors, each ancestor being a pair (lnumgen, rnumgen)
		assumes independence of material derived from each ancestor """
	return max(halfcousinLength(chrnum, lnum, rnum) for lnum, rnum in ancestors)

def descendentChrome(chrome, numgen):
	for spam in xrange(numgen):
		chrome = childChrome(chrome)
	return chrome

def descendentLength(chrnum, numgen):
	"""expected max. length of shared material between node and descendent"""
	return maxLength(descendentChrome(Chromosome(chrnum), numgen).top)

def makePlot(sampleThunk, bucketlen=1000, numsamples=10000):
	chromesamples = [[sampleThunk(chrnum) for spam in xrange(numsamples/10)] \
					for chrnum in xrange(1, 23)]
	samples = [int(max(random.choice(cs) * 3e6 for cs in chromesamples)) \
				for spam in xrange(numsamples)]
	print samples
	hist = utils.getHist([int(x+bucketlen/2)/bucketlen * bucketlen for x in samples])
	return 	[bucketlen * x for x in xrange(max(samples) / bucketlen)],\
			[float(hist.get(bucketlen * x, 0)) / numsamples \
					for x in xrange(max(samples) / bucketlen)]

#top = ((0,1),(0,1))
#regionsim.makePlot(partial(regionsim.descendentLength, chrome=top, numgen=3))
#pylab.plot(*regionsim.makePlot(partial(regionsim.cousinLength, lnumgen=5, rnumgen=5)))
#pylab.plot(*regionsim.makePlot(partial(regionsim.relativeLength, ancestors=[(4,4), (4,4)]), numsamples=10000))

