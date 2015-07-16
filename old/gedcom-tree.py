#!/usr/bin/python
from __future__ import with_statement

import sys, re, operator, math, string, os.path, hashlib, random, itertools, os

from functools import *
from itertools import *

import status, utils #, graphing
from pype import *

import common

MALE, FEMALE = "male", "female"

def parseGED(filename):
    with open(filename) as f:
        curblock = []
        inblock = False
        for line in f:
            if line.startswith('0') and len(curblock) > 0:
                yield curblock
                curblock = []
                inblock = False
            if re.search('0.*FAM', line):
                inblock = True
            if inblock:
                match = re.match('1 (HUSB|WIFE|CHIL) @(....*)@', line)
                if match:
                    nodetype, nodeid = match.groups()
                    curblock.append((nodetype, nodeid))

class Node(common.Node)
    pass

_allnodes = {}

def getNode(id):
    global _allnodes
    return _allnodes.setdefault(id, Node(id))

def processBlock(block):
    children = []
    dad, mom = None, None
    for nodetype, nodeid in block:
        if nodetype == 'HUSB':
            dad = getNode(nodeid)
            assert dad.sex in (MALE, None)
            dad.sex = MALE
        if nodetype == 'WIFE':
            mom = getNode(nodeid)
            assert mom.sex in (FEMALE, None)
            mom.sex = FEMALE
        if nodetype == 'CHIL':
            children.append(getNode(nodeid))

    if dad and mom:
        dad.spouses.add(mom)
        mom.spouses.add(dad)

    for child in children:
        if child.dad or child.mom: #this ensures parents are always spouses
            continue
        if dad:
            dad.children.add(child)
            child.dad = dad
        if mom:
            mom.children.add(child)
            assert child.mom in (mom, None)
            child.mom = mom

def readData():
    gedfiles = os.popen('ls data | grep family') | pStrip | pList
    for filename in gedfiles:
        map(processBlock, parseGED('data/' + filename))
        status.status(total=len(gedfiles))

def main():
    global _opts
    _opts, args = utils.EasyParser("").parse_args()

if __name__ == "__main__": main()
