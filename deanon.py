#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random

from scipy import signal

from functools import *
from itertools import *

import status, utils, graphing
from pype import *
from pypethread import *

import mate, common

XMAX = 20

def sampleFromPdfVector(vector):
	"""note: max running time is O(len(vector)), but usually much faster"""
	maxval = max(vector)
	assert maxval > 0
	while True:
		x = random.randrange(len(vector))
		if random.random() < vector[x] / maxval:
			return x

def convolveSequence(vectors):
	return reduce(lambda u, v: signal.fftconvolve(u, v)[:len(u)], vectors)

def convolvedDensity(relation):
	"""TODO: cache"""
	def pdfVectors():
		for (h1, h2), val in relation.iteritems():
			dist = h1 + h2
			for spam in xrange(val):
				yield pdfvectors[dist]
	return convolveSequence(pdfVectors())

def nodeDepth(node):
	if not node.dad:
		return 0
	return nodeDepth(node.dad) + 1

def individualScores(relative, relation, sample):
	"""sample is specified as an array index"""
	pair = relation.keys()[0]
	nodeheight = pair[0]-pair[1]
	relmap = common.relationMap(relative, min(8, 9-nodeheight))
	scores = {}
	for possiblevictim, rel in relmap.iteritems():
		h1, h2 = rel.keys()[0]
		if abs(h1 - h2) > 3 or h1 + h2 < 2:
			continue
		scores[possiblevictim] = convolvedDensity(rel)[sample]
		#sys.stderr.write("%.5f\n" % max(convolvedDensity(rel)))
	meanscore = utils.mean(scores.itervalues())
	maxscore = max(scores.itervalues())
	return ((k, val / meanscore * maxscore ** 0.3)) | pDict()

def aggregateScores(node):
	relmap = common.relationMap(node)
	scores = {}
	totallen = sum(1 for n in relmap if n.ispublic)
	for relative, relation in relmap.iteritems():
		if not relative.ispublic:
			continue
		ibdsample = sampleFromPdfVector(convolvedDensity(relation))
		for k, s in individualScores(relative, relation, ibdsample):
			scores[k] = scores.get(k, 0) + s
		status.status(total=totallen)
	return scores


def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
