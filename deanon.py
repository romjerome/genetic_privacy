#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, array, numpy, shelve, cPickle

import simplejson as json

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

class SiblingError(Exception):
	pass

def aggregateScores(node):
	relmap = common.relationMap(node)
	scores = {}
	totallen = sum(1 for n in relmap if n.ispublic)
	ibdsamples = {}
	for relative, relation in relmap.iteritems():
		if not relative.ispublic:
			continue
		h1, h2 = relation.keys()[0]
		if min(map(sum, relation.keys())) < 2:
			raise SiblingError
		ibdsample = ibdsamples[relative] = \
				sampleFromPdfVector(cached.convolvedDensity(relation))
		if ibdsample == 0:
			continue
		for k, s in individualScores(node, relative, relation, ibdsample).iteritems():
			# total score is L-p norm
			scores.setdefault(k, []).append(s ** 0.5) 
	return scores, ibdsamples

def nonmatchScore(vic, cand, publicnodes, scores, ibdsamples):
	#candmap = common.relationMap(cand)
	def zeroProb(node):
		"""prob that i.b.d. of node and cand is zero"""
		relation = common.relationMap(node).get(cand)
		return cached.convolvedDensity(relation)[0] if relation else 1.0
	product = lambda seq: reduce(operator.__mul__, seq, 1.0)
	return product(zeroProb(n) for n in publicnodes if not ibdsamples.get(n))
	#return product(zeroProb(r) for n, r in candmap.iteritems()
	#				if n.ispublic and not ibdsamples.get(n))



def smallestDistance(n1, n2):
	"""this is inefficient but the hope is that it will be amortized by the 
	cache in relationMap"""
	if n1 == n2:
		return 0
	if n2 not in common.relationMap(n1):
		return None
	relation = common.relationMap(n1)[n2]
	return min(abs(h1 + h2) for h1, h2 in relation.keys())

def analyzeScores(node, scores, ibdsamples, publicnodes):
	result = utils.JStruct()
	highscores = dict((k, s) for k, s in scores.items() if sum(s) >= sum(scores[node]))
	result.num_cands = len(highscores)
	siblinggroups = set(frozenset(k.dad.children & k.mom.children) for k in highscores)
	groupreps = utils.permute(
		[node if node in group else list(group)[0] for group in siblinggroups])
	groupreps = filter(lambda r: nonmatchScore(node, r, publicnodes, scores, ibdsamples) > 0.1, groupreps)
	result.num_groups_unfiltered = len(siblinggroups)
	result.num_groups = len(groupreps)
	result.distances = [smallestDistance(node, rep) for rep in groupreps]
	try:
		result.generations = map(lambda n:n.generation, groupreps)
	except AttributeError:
		pass
	result.num_relatives = sum(1 for r in common.relationMap(node) if r.ispublic)
	result.num_matching_relatives = len(scores[node])
	result.cand_num_rel_hist = map(lambda n: len(scores[n]), groupreps) | pHist()
	return result
	#TODO: eccentricity

def doSample(tree, publicnodes, numsamples=5):
	vic = random.choice(tree[-1])
	#scores, ibdsamples = aggregateScores(vic)
	return [analyzeScores(vic, *aggregateScores(vic), publicnodes=publicnodes) for spam in xrange(numsamples)]

def makePopulation(size=100000, generations=10, public_prob=0.002, public_gens=4):
	tree = mate.makeTree(size, generations)
	for node in tree[:-public_gens] | pFlatten:
		node.ispublic = False
		node.isalive = False
	for node in tree[-public_gens:] | pFlatten:
		node.ispublic = random.random() <  public_prob
		node.isalive = True
	publicnodes = tree[-public_gens:] | pFlatten | Filter(lambda n: n.ispublic) | pSet
	for node in status.wrap(publicnodes): #warm up cache
		common.relationMap(node)
	return tree, publicnodes

def driver():
	params = json.load(open(_opts.infile))
	tree, publicnodes = makePopulation(**dict(map(lambda (k, v): (str(k), v), 
											params['population'].items())))
	results = {'params': params, 'victims' :  []}
	for spam in xrange(params['num_victims']):
		results['victims'].append(doSample(tree, publicnodes, params['samples_per_victim']))
	with open(_opts.outfile,  'w') as outfile:
		outfile.write(json.dumps(results, indent=2))

def main():
	global _opts
	_opts, args = utils.EasyParser("infile=deanon.in: outfile=deanon.out:").parse_args()
	driver()
	#_opts.shelf = shelve.open(_opts.outfile, protocol=cPickle.HIGHEST_PROTOCOL)

if __name__ == "__main__": main()
