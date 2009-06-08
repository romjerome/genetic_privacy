from __future__ import with_statement
# test self-correlation and cross-correlation between people

import sys, re, operator, math, string, os.path, hashlib, random, itertools, numpy

from functools import *
from itertools import *

import status, utils
from pype import *

#one chromosome of one individual
class Chromosome:
	def __init__(self, person, chr_id, txtdata):
		self.person = person
		self.chr_id = chr_id
		data = [int(x) for x in txtdata if x in "01"]
		self.data = numpy.array(data,numpy.bool)

class Person:
	def __init__(self, id):
		self.id = id
		self.chromosomes = {}


def readChromosome(filename, chr_id, persons):
	with open(filename) as infile:
		for person in persons:
			txtdata = infile.readline()
			infile.readline() #ignore every alternate row
			person.chromosomes[chr_id] = Chromosome(person, chr_id, txtdata)
		
		assert infile.read() == ''

def compareRegions(lchrome, rchrome, numregions):
	#returns number of exactly matching regions
	regionlen = ((len(lchrome.data)-1) / numregions) + 1
	return len([None for idx in xrange(numregions) if 
			numpy.all(lchrome.data[idx*regionlen:(idx+1)*regionlen] == \
			rchrome.data[idx*regionlen:(idx+1)*regionlen])])

def correlation(lchrome, rchrome):
	return sum(lchrome.data == rchrome.data)

def selfCorrelation(persons, chr_id=1):
	values = [correlation(p.chromosomes[chr_id], p.chromosomes[chr_id]) \
				for p in persons]
	return utils.mean(values)

def crossCorrelation(persons, chr_id=1, correlation=correlation):
	indices = [(p, q) for (p, q) in utils.crossProduct(persons, persons) if p.id < q.id]
	values = []
	for p, q in indices:
		values.append(float(correlation(p.chromosomes[chr_id], q.chromosomes[chr_id])))
		status.status(total=len(indices))
	print values
	return utils.mean(values), utils.stdDev(values)

if __name__ == "__main__":
	persons = [test.Person(i) for i in xrange(60)]
	test.readChromosome('data/chr1', 1, persons)
	crossCorrelation(persons[:20], correlation=partial(test.compareRegions, numregions=100))
	
