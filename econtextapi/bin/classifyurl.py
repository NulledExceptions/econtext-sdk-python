#! /usr/bin/python

usage = """
Quickly classify lots of social posts by distributing across multiple processors.

Input file should be a simple text file with one social post per line.

Be careful not to use too many workers at once - at some point it will end up
putting too much pressure on the API.  Use common sense.
"""

import argparse
import requests
import sys
import logging
import json
import csv
import time

import multiprocessing
from econtextapi.client import Client
from econtextapi.classify import Url

log = logging.getLogger('econtext')

def get_log_level(v=0):
    if v is None or v == 0:
        return logging.ERROR
    elif v > 1:
        return logging.DEBUG
    elif v > 0:
        return logging.INFO

def get_log(v):
    log_level = get_log_level(v)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("%(process)s - %(asctime)s - %(levelname)s :: %(message)s", "%Y-%m-%d %H:%M:%S"))
    log.addHandler(h)
    h.setLevel(log_level)
    log.setLevel(log_level)

def f(x):
    """
    classify a set of social posts and block until you get the results - print 
    them when you get the output
    
    @param x: a list of up to 1000 posts
    """
    section, classify = x
    log.debug("classify/url with {} url".format(classify.classify_data))
    response = classify.classify()
    return section, response

def ff(x):
    return "ff(x): {}".format(x)


def main():
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("-i", "--in", dest="infile", default="stdin", help="Input file", metavar="PATH")
    parser.add_argument("-o", "--out", dest="outfile", default="stdout", help="Output file", metavar="PATH")
    parser.add_argument("-u", dest="username", required=True, action="store", default=None, help="API username")
    parser.add_argument("-p", dest="password", required=True, action="store", default=None, help="API password")
    parser.add_argument("-w", dest="workers", action="store", default=1, help="How many worker processes to use")
    parser.add_argument("-v", dest="config_verbose", action="count", default=0, help="Be more or less verbose")
    options = parser.parse_args()
    get_log(options.config_verbose)
    
    log.info("Running classification using {} worker processes".format(options.workers))
    
    if options.infile == 'stdin':
        infile = sys.stdin
    else:
        infile = open(options.infile, 'r')
    if options.outfile == 'stdout':
        outfile = sys.stdout
    else:
        outfile = open(options.outfile, 'w')
    
    urls = [k.strip() for k in infile]
    log.info("Total URLs: {}".format(len(urls)))
    
    client = Client(options.username, options.password)
    poolInput = ((i, Url(client, urls[i])) for i in range(0, len(urls)))

    start = time.time()
    p = multiprocessing.Pool(processes=int(options.workers))
    resultset = p.imap_unordered(f, poolInput)
    
    s = 0
    with outfile as file:
        for (section, listitem) in resultset:
            s = s + 1
            log.debug("Processing set {}".format(section+1))
            listitem.result["url"] = urls[section]
            file.write("{}\n".format(json.dumps(listitem.result)))
    
    elapsed = time.time()-start
    log.info("Total time: {}".format(elapsed))
    log.info("Total urls: {}".format(s))
    log.info("Time per url: {}".format(elapsed/(s+.000000001)))
    return True
    

if __name__ == "__main__":
    main()
