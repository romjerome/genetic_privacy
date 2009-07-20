from __future__ import with_statement

"""computes expected characteristics (e.g, max. length) of 
shared contiguous regions across simulated meiosis for arbitrarily related humans"""

import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy, array

from scipy import integrate

from functools import *
from itertools import *

import status, utils
from pype import *

from chrlen import chromelengths, geneticlengths

TOP, BOT = 0, 1

#def gammaDensity(x, nu=4.3):
#	return math.exp(-2*nu*x) * (2*nu)**nu * x**(nu-1) /  8.85
#
#def pdfSample(f, interval, epsilon=1e-6):
#	unisample = random.random()
#	xmin, xmax = map(float, interval)
#	f_int = lambda x: integrate.quad(f, interval[0], x)[0]
#	inttable = {}
#	get_int = lambda x: inttable.setdefault(x, f_int(x))
#	while xmax - xmin > epsilon:
#		xmid = (xmax + xmin) / 2
#		if integrate.quad(f, interval[0], xmid)[0] > unisample:
#			xmax = xmid
#		else:
#			xmin = xmid
#	return (xmax + xmin) / 2
#
#gammaSample = partial(pdfSample, f=gammaDensity, interval=(0, 10)) #10 is infinity

gammasamples = array.array('f')
gammasamples.fromfile(open('../data/gammasamples'), 100000) #FIXME: data_dir

def gammaSample():
	return random.choice(gammasamples)

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
					tostrand2.append((which, locus, right))
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

def strandProperty(strand, property):
	lengths = map(lambda (w, l, r): r-l, strand)
	return property(lengths)

def halfcousinProperty(chrnum, lnumgen, rnumgen, property):
	"""	expected characteristic of shared material in half-cousins with a single common
		ancestor lnumgen and rnumgen generations above, respectively"""
	lstrand = descendentChrome(Chromosome(chrnum), lnumgen).top
	rstrand = descendentChrome(Chromosome(chrnum), rnumgen).top
	return strandProperty(intersectStrands(lstrand, rstrand), property)

def relativeProperty(chrnum, ancestors, property=sum):
	"""	expected characteristic of shared material in relatives who share a list
		of ancestors, each ancestor being a pair (lnumgen, rnumgen)
		assumes independence of material derived from each ancestor """
	return property(halfcousinProperty(chrnum, lnum, rnum, property) for lnum, rnum in ancestors)

def descendentChrome(chrome, numgen):
	for spam in xrange(numgen):
		chrome = childChrome(chrome)
	return chrome

def descendentProperty(chrnum, numgen, property=sum):
	"""expected max. length of shared material between node and descendent"""
	return strandProperty(descendentChrome(Chromosome(chrnum), numgen).top, property)

def getPdf(sampleThunk, bucketsize, numsamples):
	chromesamples = [[sampleThunk(chrnum) for spam in xrange(numsamples/10)] \
					for chrnum in xrange(1, 23)]
	samples = [sum(random.choice(s) for s in chromesamples) for spam in xrange(numsamples)]
	return utils.getHist(int(x * bucketsize) for x in samples)

def makePlot(sampleThunk, bucketsize=100.0, numsamples=10000):
	hist = getPdf(sampleThunk, bucketsize, numsamples)

	xs = range(int(max(hist.keys())+1))
	ys = [float(hist.get(x, 0.0)) / numsamples * bucketsize for x in xs]
	return 	[x/float(bucketsize) for x in xs], ys[:1] + list(utils.iirSmooth(ys[1:], 0.1))

#top = ((0,1),(0,1))
#regionsim.makePlot(partial(regionsim.descendentProperty, chrome=top, numgen=3))
#pylab.plot(*regionsim.makePlot(partial(regionsim.cousinLength, lnumgen=5, rnumgen=5)))
#pylab.plot(*regionsim.makePlot(partial(regionsim.relativeLength, ancestors=[(4,4), (4,4)]), numsamples=10000))

