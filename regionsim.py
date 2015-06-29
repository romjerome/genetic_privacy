from __future__ import with_statement

"""computes expected characteristics (e.g, max. length) of
shared contiguous regions across simulated meiosis for arbitrarily related humans"""

import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy, array

from scipy import integrate, signal

from functools import *
from itertools import *

import status, utils
from pype import *

import common
from chrlen import chromelengths, geneticlengths

TOP, BOT = 0, 1

#def gammaDensity(x, nu=4.3):
#       return math.exp(-2*nu*x) * (2*nu)**nu * x**(nu-1) /  8.85
#
#def pdfSample(f, interval, epsilon=1e-6):
#       unisample = random.random()
#       xmin, xmax = map(float, interval)
#       f_int = lambda x: integrate.quad(f, interval[0], x)[0]
#       inttable = {}
#       get_int = lambda x: inttable.setdefault(x, f_int(x))
#       while xmax - xmin > epsilon:
#               xmid = (xmax + xmin) / 2
#               if integrate.quad(f, interval[0], xmid)[0] > unisample:
#                       xmax = xmid
#               else:
#                       xmin = xmid
#       return (xmax + xmin) / 2
#
#gammaSample = partial(pdfSample, f=gammaDensity, interval=(0, 10)) #10 is infinity

gammasamples = array.array('f')
gammasamples.fromfile(open(common.data_dir + '/gammasamples'), 100000)

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
    """ crossover on genetic lengths according to Broman-Weber
            chromosome from specified parent is always top
    """
    top, bot = chrome.top, chrome.bot
    #if len(top) == 0 and len(bot) == 0:
    #       return Chromosome(chrome.number, [], [])
    for locus in recombLoci(geneticlengths[chrome.number]):
        newtop, newbot = [], []

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
def matchStrands(lstrand, rstrand):
    for lwhich, lleft, lright in lstrand:
        for rwhich, rleft, rright in rstrand:
            if lwhich is None and rwhich is not None:
                lwhich = rwhich
            elif rwhich is None and lwhich is not None:
                rwhich = lwhich
            elif lwhich != rwhich:
                continue
            if rright < lleft or lright < rleft:
                continue
            yield (lwhich, max(lleft, rleft), min(lright, rright))

def strandProperty(strand, property):
    lengths = map(lambda (w, l, r): r-l, strand)
    return property(lengths)

def gammaSelfIntersection(geneticlength, numgen):
    @utils.materialize
    def intersectIntervals(intervals):
        START, END = 0, 1
        combinedloci = intervals | pFlatten |\
                                        Map(lambda (st, end): [(st, START), (end, END)]) |\
                                        pFlatten | pSort()
        nesting = 0
        prev = None
        for pos, which in combinedloci:
            if nesting == len(intervals) and which == END:
                yield (prev, pos)
            nesting += (1 if which == START else -1)
            if nesting == len(intervals):
                prev = pos

    if numgen == 0:
        return [(None, 0, geneticlength)]

    recombloci = [[0] + list(recombLoci(geneticlength)) + [geneticlength]\
                                            for spam in xrange(numgen)]
    intervals = [zip(loci, loci[1:])[random.randrange(2)::2] for loci in recombloci]
    return [(None, st, end) for st, end in intersectIntervals(intervals)]

"""
a property is a function with two behaviors
 - if called on two args it aggregates over the two args
 - if called with one arg, it aggregates over the items of that arg
"""

maxLength = lambda *args: max(args[0] + [0]) if len(args) == 1 else max(args)
totalLength = lambda *args: sum(args[0]) if len(args) == 1 else sum(args)
segmentCount = lambda *args: len(args[0]) if len(args) == 1 else sum(args)
countAndLength = \
                lambda *args:   (len(args[0]), sum(args[0])) \
                                                        if len(args) == 1\
                                                else (len(args), sum(arg[1] for arg in args))

#def countAndLength(*args):
#       if len(args) == 1: # leaf; values are lengths
#               n = len(args[0])
#               l = sum(args[0])
#else: # internal node; values are pairs
#               n = len(args)
#               l = sum([arg[1] for arg in args])
#       return (n, l)

def halfcousinProperty(chrnum, lnumgen, rnumgen, property):
    """     expected characteristic of shared material in half-cousins with a single common
            ancestor lnumgen and rnumgen generations above, respectively"""
    if lnumgen > rnumgen:
        lnumgen, rnumgen = rnumgen, lnumgen
    lstrand = descendentStrand(Chromosome(chrnum), lnumgen)
    rstrand = descendentStrand(Chromosome(chrnum), rnumgen)
    if lnumgen == 0:
        lstrand1 = Chromosome(chrnum).top
        lstrand2 = Chromosome(chrnum).bot
        prop1 = strandProperty(matchStrands(lstrand1, rstrand), property)
        prop2 = strandProperty(matchStrands(lstrand2, rstrand), property)
        return property(prop1, prop2)
    return strandProperty(matchStrands(lstrand, rstrand), property)

def relativeProperty(chrnum, ancestors, property=totalLength):
    """     expected characteristic of shared material in relatives who share a list
            of ancestors, each ancestor being a pair (lnumgen, rnumgen)
            assumes independence of material derived from each ancestor """
    return property(halfcousinProperty(chrnum, lnum, rnum, property) for lnum, rnum in ancestors)

#def descendentChrome(chrome, numgen):
#       for spam in xrange(numgen):
#               chrome = childChrome(chrome)
#       return chrome

def descendentStrand(chrome, numgen):
    childstrand = childChrome(chrome).top
    selfintersection = gammaSelfIntersection(geneticlengths[chrome.number], numgen-1)
    return matchStrands(childstrand, selfintersection)

def descendentProperty(chrnum, numgen, property=totalLength):
    """expected max. length of shared material between node and descendent"""
    return strandProperty(descendentStrand(Chromosome(chrnum), numgen), property)

def pdfVector(distance, chrnum, xmax, numbuckets, numsamples):
    """if chrnum is None, then sum over the whole genome"""
    if chrnum is None:
        vectors = (pdfVector(distance, chrnum, xmax, numbuckets, numsamples) \
                                for chrnum in xrange(1, 23))
        return reduce(lambda u, v: signal.fftconvolve(u, v)[:len(u)], vectors)

    vector = numpy.zeros(numbuckets, numpy.float32)
    for spam in xrange(numsamples):
        sample = relativeProperty(chrnum, [(1, distance-1)])
        vector[int(sample * numbuckets / xmax)] += 1.0/numsamples
    return vector

def pdfHist(sampleThunk, bucketsize, numsamples, property=totalLength):
    """pdf histogram for the whole genome"""
    chromesamples = [[sampleThunk(chrnum) for spam in xrange(numsamples/10)] \
                                    for chrnum in xrange(1, 23)]
    samples = [property(random.choice(s) for s in chromesamples) for spam in xrange(numsamples)]
    return utils.getHist(int(x  / bucketsize) for x in samples)


def makePlot(sampleThunk, bucketsize=0.02, numsamples=10000, property=totalLength, ignorezero=True):
    hist = pdfHist(sampleThunk, bucketsize, numsamples, property)
    if ignorezero:
        del hist[0]

    xs = range(int(max(hist.keys())+1))
    ys = [float(hist.get(x, 0.0)) / numsamples / bucketsize for x in xs]
    return  [x * float(bucketsize) for x in xs], ys[:1] + list(utils.iirSmooth(ys[1:], 0.1))

#top = ((0,1),(0,1))
#regionsim.makePlot(partial(regionsim.descendentProperty, chrome=top, numgen=3))
#pylab.plot(*regionsim.makePlot(partial(regionsim.cousinLength, lnumgen=5, rnumgen=5)))
#pylab.plot(*regionsim.makePlot(partial(regionsim.relativeLength, ancestors=[(4,4), (4,4)]), numsamples=10000))
