#!/usr/bin/python
from __future__ import with_statement

import re, os.path, urllib2, time, socket, glob, httplib

from functools import *
from itertools import *

import status, utils
from pype import *

family_url_prefix = \
        'http://www.familysearch.org/eng/search/AF/family_group_record.asp?familyid=%s'
gedcom_url_prefix = \
        'http://www.familysearch.org/Eng/Search/AF/family_group_record_gedcom.asp?familyid=%s'
indiv_url_prefix = \
        'http://www.familysearch.org/eng/search/AF/individual_record.asp?recid=%s'

data_dir = 'data/'

wait_time = 1 #seconds

socket.setdefaulttimeout(5)

scrapedids = os.popen('ls data | grep afnmap | sed "s/.afnmap//"') | pStrip | pSet
scrapequeue = os.popen('ls data | grep family | sed "s/.family//"') | pStrip | pSet
scrapequeue -= scrapedids
scrapedrecids = open(data_dir + 'scrapedrecs') | pStrip | pSet

@utils.failSilently(exception=(urllib2.URLError, socket.timeout, httplib.BadStatusLine))
def urlRead(url):
    return urllib2.urlopen(url).read()

def makeMap(familyid):
    """recid -- AFN mapping"""
    data = urlRead(family_url_prefix % familyid)
    if data is None:
        return

    def pairs():
        for line in data.split('\n'):
            match = re.search('recid=([0-9]*)[^0-9].*\(AFN:(.*)\)', line)
            if match:
                yield match.groups()[1], match.groups()[0]
    afnmap = dict(pairs())

    with open(data_dir + familyid + '.afnmap', 'w') as out:
        for afn, recid in afnmap.iteritems():
            out.write("%s %s\n" % (afn, recid))

    return afnmap

def scrapeRecord(recid):
    data = urlRead(indiv_url_prefix % recid)
    if data is None:
        return

    for line in data.split('\n'):
        match = re.search('family_group_record.asp\?familyid=([0-9]*)[^0-9]', line)
        if match:
            yield match.groups()[0]

def processRecord(recid, qout, scrout):
    global scrapedrecids
    qout.write('\n'.join(set(scrapeRecord(recid))) + '\n')
    qout.flush()
    scrout.write(recid + '\n')
    scrout.flush()
    scrapedrecids.add(recid)

processRecord = partial(processRecord,
                                                qout=open(data_dir + 'crawlqueue.in', 'a'),
                                                scrout = open(data_dir + 'scrapedrecs', 'a'))

def processMissedRecords():
    """get records that were missed because of server errors"""
    allrecids = glob.iglob(data_dir + '*afnmap') | Map(lambda f: open(f) | pCut(1)) | pFlatten | pSet
    missedids = allrecids - scrapedrecids
    for id in missedids:
        processRecord(id)
        time.sleep(_opts.waittime)
        status.status('missed ids', total=len(missedids))

def main():
    global _opts
    _opts, args = utils.EasyParser("waittime=1.0: missed").parse_args()

    if _opts.missed:
        processMissedRecords()

    for familyid in scrapequeue:
        themap = makeMap(familyid)
        time.sleep(_opts.waittime)
        if themap is None:
            themap = {}
        for recid in themap.itervalues():
            if recid in scrapedrecids:
                continue
            processRecord(recid)
            time.sleep(_opts.waittime)
        status.status(total=len(scrapequeue))

    qout.close()
    scrout.close()

if __name__ == "__main__":
    main()
