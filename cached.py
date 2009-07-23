#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, array, numpy

from scipy import signal

from functools import *
from itertools import *

import status, utils, graphing
from pype import *
from pypethread import *

#TODO: truncate the vectors

VECTORLEN = 20000

def truncateNonzero(vector):
	"""hack to determine nonzero range of the array"""
	trunclen = numpy.argmin(numpy.greater(vector, 1e-8))
	if trunclen == 0:
		return vector
	return vector[:trunclen]

pdfvectors = {}
for d in xrange(2, 14):
	a = array.array('f')
	# FIXME: data_dir
	a.fromfile(
			open('../data/distance=%d,xmax=20,numbuckets=20000.pdfvector' % d),
			VECTORLEN)
	pdfvectors[d] = truncateNonzero(numpy.array(a, numpy.float32))

def convolveSequence(vectors):
	return reduce(lambda u, v: truncateNonzero(signal.fftconvolve(u, v)), vectors)

#TODO: write a cache decorator

def convolvedDensity(relation_or_distseq):
	cache = utils.getattrdefault(convolvedDensity, 'cache', dict)
	if hasattr(relation_or_distseq, "items"):
		distseq = 	relation_or_distseq.iteritems() |\
					Map(lambda ((h1, h2), val): (h1 + h2 for spam in xrange(val))) |\
					pFlatten | pSort() | Sink(tuple)
		if distseq in cache:
			return cache[distseq]
		subseqs = [tuple([d for d in distseq if d == i]) for i in set(distseq)]
		vectors = map(convolvedDensity, subseqs)
	else:
		distseq = relation_or_distseq
		if distseq in cache:
			return cache[distseq]
		vectors = map(pdfvectors.get, distseq)
	print distseq
	cache[distseq] = convolveSequence(vectors)
	return cache[distseq]

