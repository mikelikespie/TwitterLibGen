#!/usr/bin/env python

import BeautifulSoup
import sys
import urllib2

soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(sys.argv[1]))
for link in soup(name='a'):
    if link(text=lambda t: '/' in t):
            print 'http://apiwiki.twitter.com' + link['href']
