#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, array, numpy

from scipy import signal

from functools import *
from itertools import *

import status, utils, graphing
from pype import *
from pypethread import *

pdfvectors = {}
for d in xrange(2, 14):
	a = array.array('f')
	# FIXME: data_dir
	a.fromfile(open('../data/distance=%d,xmax=20,numbuckets=20000.pdfvector' % d), 20000)
	pdfvectors[d] = numpy.array(a, numpy.float32)

def convolveSequence(vectors):
	return reduce(lambda u, v: signal.fftconvolve(u, v)[:len(u)], vectors)

def convolvedDensity(relation):
	cache = utils.getattrdefault(convolvedDensity, 'cache', dict)
	distseq = 	relation.iteritems() |\
				Map(lambda ((h1, h2), val): (h1 + h2 for spam in xrange(val))) |\
				pFlatten | pSort() | Sink(tuple)
	if distseq not in cache:
		print distseq
		cache[distseq] = convolveSequence(map(pdfvectors.get, distseq))
	return cache[distseq]


