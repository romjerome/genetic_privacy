#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, array, numpy

from scipy import signal

from functools import *
from itertools import *

import status, utils, graphing
from pype import *
from pypethread import *

import mate, common, cached

XMAX = 20

def sampleFromVector(vector):
	"""note: max running time is O(len(vector)), but usually much faster"""
	maxval = max(vector)
	assert maxval > 0
	while True:
		x = random.randrange(len(vector))
		if random.random() < vector[x] / maxval:
			return x

def sampleFromPdfVector(vector):
	"""assumes that a lot of the weight is at 0"""
	#FIXME: cached.pdfvectors[2] doesn't sum to 1
	#if random.random() < 0.001:
	#	assert 0.99 < sum(vector) < 1.01
	if random.random() < vector[0]:
		return 0
	return sampleFromVector(vector[1:])

def nodeDepth(node):
	"""just for testing. assumes generational integrity"""
	if not node.dad:
		return 0
	return nodeDepth(node.dad) + 1

def nodeHeight(node):
	"""just for testing. assumes generational integrity"""
	if not node.children:
		return 0
	return nodeHeight(list(node.children)[0]) + 1

def individualScores(victim, relative, relation, sample):
	"""sample is specified as an array index"""
	global _node, _rel
	pair = relation.keys()[0]
	nodeheight = pair[0]-pair[1]
	relmap = common.relationMap(relative, min(8, 9-nodeheight))
	if victim not in relmap:
		_node = victim
		_rel = relative
		assert False
	scores = {}
	for possiblevictim, relation in relmap.iteritems():
		h1, h2 = relation.keys()[0]
		if abs(h1 - h2) > 3 or min(map(sum, relation.keys())) < 2:
			continue
		pdfvector = cached.convolvedDensity(relation)
		scores[possiblevictim] = pdfvector[sample] if sample < len(pdfvector) else 0
	meanscore = utils.mean(scores.itervalues())
	maxscore = max(scores.itervalues())
	return dict(((k, val / maxscore) for k, val in scores.iteritems()))

def aggregateScores(node):
	relmap = common.relationMap(node)
	scores = {}
	totallen = sum(1 for n in relmap if n.ispublic)
	for relative, relation in relmap.iteritems():
		if not relative.ispublic:
			continue
		status.status(total=totallen)
		h1, h2 = relation.keys()[0]
		assert min(map(sum, relation.keys())) >= 2
		ibdsample = sampleFromPdfVector(cached.convolvedDensity(relation))
		if ibdsample == 0:
			continue
		for k, s in individualScores(node, relative, relation, ibdsample).iteritems():
			# total score is L-0.5 norm
			scores.setdefault(k, []).append(s ** 0.5) 
	return scores

def smallestDistance(n1, n2):
	"""this is inefficient but the hope is that it will be amortized by the 
	cache in relationMap"""
	if n2 not in common.relationMap(n1):
		return None
	relation = common.relationMap(n1)[n2]
	return min(abs(h1 + h2) for h1, h2 in relation.keys())

def analyzeScores(node, scores):
	result = utils.JStruct()
	highscores = dict((k, s) for k, s in scores.items() if sum(s) >= sum(scores[node]))
	result.num_cands = len(highscores)
	siblinggroups = set(frozenset(k.dad.children & k.mom.children) for k in highscores)
	groupreps = utils.permute([list(group)[0] for group in siblinggroups])
	result.num_groups = len(siblinggroups)
	result.distances = [smallestDistance(node, rep) for rep in groupreps]
	result.heights = [map(nodeHeight, groupreps)]
	result.num_relatives = sum(1 for r in common.relationMap(node) if r.ispublic)
	result.num_matching_relatives = len(scores[node])
	result.cand_num_rel_hist = map(lambda n: len(scores[n]), groupreps) | pHist()
	#result.cand_num_mat_rel_hist = map(lambda n: sum(1 -  for r in common.relationMap(n) if r.ispublic))
	return result
	#TODO: eccentricity
	#TODO: negative scores when candidate should have matched a relative but didn't

def main():
	global _opts
	_opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
