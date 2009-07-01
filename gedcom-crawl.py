#!/usr/bin/python
from __future__ import with_statement

"""crawls the family records of the LDS ancestry file

produces output in data/<id>.family

start it by appending ids to data/crawlqueue"""

import sys, re, operator, math, string, os.path, hashlib, random, itertools, urllib2, time, socket

from functools import *
from itertools import *

import status, utils
from pype import *

gedcom_url_prefix = 'http://www.familysearch.org/Eng/Search/AF/family_group_record_gedcom.asp?familyid=%s'

start_id = '7366709'

data_dir = 'data/'

wait_time = 1 #seconds

socket.setdefaulttimeout(5)


crawledids = open('data/crawledids') | pStrip | pSet
crawlqueue = open('data/crawlqueue') | pStrip | Filter(lambda id: id not in crawledids) | pList
seenids = crawledids | set(crawlqueue)
origcrawlcount = len(crawledids)

def parseIds(data):
	"""grab the family id's from a piece of gedcom data"""
	for line in data.split('\n'):
		match = re.search('FAMC.*@F(.*)@', line)
		if match:
			yield match.groups()[0]

def doStep(id=None):
	"""if id is None, then an id will be pulled out of crawlqueue"""
	global crawlqueue, seenids
	if id is None:
		id, crawlqueue = crawlqueue[0], crawlqueue[1:]
	assert id not in crawledids
	try:
		data = urllib2.urlopen(gedcom_url_prefix % id).read()
	except urllib2.URLError: # timeout
		return

	crawledids.add(id)
	with open('data/crawledids', 'a') as out:
		out.write(id + '\n')

	if data.startswith('No records found'):
		return

	with open(data_dir + id + '.family', 'w') as out:
		out.write(data)

	newids = set(parseIds(data)) - seenids
	
	crawlqueue.extend(newids)
	with open('data/crawlqueue', 'a') as out:
		for newid in newids:
			out.write(newid + '\n')
	
	seenids |= newids
	
	sys.stderr.write("%d crawled (%d new), %d in queue     \r" % \
			(len(crawledids), len(crawledids) - origcrawlcount, len(crawlqueue)))

	time.sleep(wait_time)

def main():
	while len(crawlqueue) > 0 and not os.path.exists('STOP'):
		doStep()
	print

if __name__ == "__main__":
	main()
