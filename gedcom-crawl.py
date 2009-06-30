#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, itertools, urllib2

from functools import *
from itertools import *

import status, utils
from pype import *

gedcom_url_prefix = 'http://www.familysearch.org/Eng/Search/AF/family_group_record_gedcom.asp?familyid=%s'

start_id = '7366709'

data_dir = 'data/'

wait_time = 1 #seconds

crawledids = open('data/crawledids') | pStrip | pSet
crawlqueue = open('data/crawlqueue') | pStrip | Filter(lambda id: id not in crawledids) | pList
seenids = crawledids | set(crawlqueue)
origcrawlcount = len(crawledids)

def parseIds(data):
	for line in data.split('\n'):
		match = re.search('FAMC.*@F(.*)@', line)
		if match:
			yield match.groups()[0]

def doStep():
	global crawlqueue, seenids
	id, crawlqueue = crawlqueue[0], crawlqueue[1:]
	assert id not in crawledids
	data = urllib2.urlopen(gedcom_url_prefix % id).read()
	with open(data_dir + id + '.family', 'w') as out:
		out.write(data)
	newids = set(parseIds(data)) - seenids

	crawledids.add(id)
	with open('data/crawledids', 'a') as out:
		out.write(id + '\n')
	
	crawlqueue.extend(newids)
	with open('data/crawlqueue', 'a') as out:
		for newid in newids:
			out.write(newid + '\n')
	
	seenids |= newids
	
	print "%d crawled (%d new), %d in queue" % \
			(len(crawledids), len(crawledids) - origcrawlcount, len(crawlqueue))

	time.sleep(wait_time)

def main():
	while len(crawlqueue) > 0 and not os.path.exists('STOP'):
		doStep()

def __name__ == "__main__":
	main()
