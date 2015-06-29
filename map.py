#!/usr/bin/python

import sys, re, operator, math, string, os.path, hashlib, random, itertools, pygooglechart

from functools import *
from itertools import *

import status, utils #, graphing
from pype import *

statecodes=open('statecodes')|pLower|pSplit('\t')|Map(partial(map,string.strip))|pDict
for k, v in statecodes.items(): statecodes[v] = v

populations=open('statepopulations')|pLower|pSplit('\t')|Map(lambda (k,v):(statecodes[k.strip()],float(v))) |pDict

hist = open('locations') | pStrip | pLower | Map(statecodes.get) | pHist()
del hist[None]
hist = dict((k,v/populations[k]) for k,v in hist.iteritems())
hist = dict((k,v/max(hist.values())) for k,v in hist.iteritems())

chart = pygooglechart.MapChart(400,220)
chart.geo_area='usa'
chart.set_codes(hist.keys()|pSort()|pUpper|pList)
chart.set_colours(['fafafa','fafafa','ff0000'])
chart.add_data(hist.keys()|pSort()|Map(hist.get)|Map(lambda x:x**((1-x)**2))|pList)
print chart.get_url()

