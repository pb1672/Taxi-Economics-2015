#!/usr/bin/env python

###############################################################################
##
## Big Data - Final Project
## reducer1.py
## Join fares and trips and search the zipcodes using rtree
## contact: drp354@nyu.edu
##
###############################################################################

import sys

def parseInput():
    for line in sys.stdin:
        yield line.strip('\n').split('\t')
        
def reducer():
    agg = {}
    for key,values in parseInput():
        print '%s,%s' % (key,values)

if __name__=='__main__':
    reducer()
