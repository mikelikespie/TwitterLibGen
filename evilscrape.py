#!/usr/bin/env python

# Silly Twitter API scraper thingy.  Feed it a twitter api page on
# standard input
#
# ideal output follows. Currently 'response' is not generated,
# 'requires_auth' is a boolean (since most pages just say 'true' and
# 'false', and methods will only ever be a list of the first method
# found.
#
# methods = [
#         {'name':'statuses/user_timeline',
#          'methods':['GET'],
#          'limit':1,
#          'requires_auth':'user_based',
#          'response':{
#              'object':'status',
#              'cardinality':'n'},
#          'parameters':[
#              {
#                  'name':'id',
#                  'required':False},
#              {   
#                  'name':'user_id',
#                  'required':False,
#                  'type':'int'},
#              {
#                  'name':'count',
#                  'required':False,
#                  'type':'int',
#                  'min':1,
#                  'max':200},
#              {
#                  'name':'page',
#                  'required':False,
#                  'type':'int',
#                  'min':1} ]
#              }
#         ]

import BeautifulSoup
import sys
import re
import json
import urllib2
from pprint import pprint
import re

def find_name():
    baseurl = 'http://apiwiki.twitter.com/'
    url_banner = soup.find(name='b', text=lambda t: 'URL' in t)
    url = url_banner.findNext(text=lambda t: 'http' in t)
    r = re.compile(r'(http://.*twitter.com/)(.*)(.format|)')
    m = r.match(url)

    return m.group(1), m.group(2)


def find_methods():
    def is_http_method(t):
        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            if method in t:
                return True

    http_banner = soup.find(name='b', text=lambda t: 'HTTP Method' in t)
    return http_banner.findNext(text=is_http_method)

def find_limit():
    number = [None]
    def has_num_token(t):
        matchobj = re.search(r'(\d)', t)
        if matchobj:
            number[0] = matchobj.group(1)
        return matchobj
    
    limit_heading = soup.find(name='b', text=lambda t: 'API rate limited' in t)
    if limit_heading:
        limit_heading.findNext(text=has_num_token)
        return number[0]

def find_auth():
    def banner_predicate(t):
        return 'Requires Authentication' in t
        
    requires_auth = [None]
    def requires_auth_predicate(t):
        matchobj = re.search(r'(true|false)', t)
        if matchobj:
            requires_auth[0] = matchobj.group(1)
        return matchobj
    
    requiresauth = soup.find(name='b', text=banner_predicate)
    # has side effect mutating requires_auth
    requiresauth.findNext(text=requires_auth_predicate)
    return requires_auth[0]

def find_parameters():
    def banner_predicate(t):
        return 'Parameters' in t
    parameters_banner = soup.find(text=banner_predicate)
    for inner in parameters_banner.findNext('ul').contents:
        if isinstance(inner, BeautifulSoup.Tag):
            text_nodes = inner(text=True)
            name = text_nodes[0]
            tlob = ' '.join(str(x) for x in text_nodes[1:])
            if name:
                if 'Optional' in tlob:
                    yield {'name': name,
                           'required': 'false'}
                elif 'Required' in tlob:
                    yield {'name': name,
                           'required': 'true'}

all = []
for s in sys.argv[1:]:

    soup = BeautifulSoup.BeautifulSoup(urllib2.urlopen(s))
    print >>sys.stderr, s
    try:
        baseurl, name = find_name()
        all.append({'name': name,
                    'baseurl': baseurl,
                          'methods': [find_methods()],
                          'limit': find_limit(),
                          'requires_auth': find_auth(),
                          'parameters':list(find_parameters())})
    except Exception, e:
        print e


pprint(all)
