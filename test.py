from tweetgen import TweetGen, BaseOpener, BasicAuthOpener, NeedAuthException
from sys import stderr
from pprint import pprint

try:
    import simplejson as json
except ImportError:
    import json


#first, let's test some basic functionality

tg = TweetGen(BaseOpener)

#let's interrogate mike
user = "mikelikespie"

#let's give some crappy input
try:
    tg.statuses_user_timeline(omg=user)
except ValueError, e: print >> stderr, e

#woops, I got user_id and id confused
try:
    ret = json.load(tg.statuses_user_timeline(user_id=user))
except ValueError, e: print >> stderr, e

ret = json.load(tg.statuses_user_timeline(id=user))
print "+++ Got %s status messages" % len(ret)

#now, let's try page
try:
    ret = json.load(tg.statuses_user_timeline(page=-1))
except ValueError, e: print >> stderr, e

ret = json.load(tg.statuses_user_timeline(id=user, page=40))
print "+++ Got %s status messages from page 40" % len(ret)


print "Getting user info for %s" % user

#I always get user_name and screen_name confused
try:
    ret = json.load(tg.users_show(user_name=user))
except ValueError, e: print >> stderr, e

ret = json.load(tg.users_show(screen_name=user))
pprint(ret)

#look, even ordered args work
ret = json.load(tg.users_show(user))
pprint(ret['status'])

ret = json.load(tg.users_show(user, method='GET'))

#let's test to see if requiring auth works
try:
    ret = json.load(tg.statuses_followers(screen_name=user))
except NeedAuthException, e: print >> stderr, e

#ok, so we need a new object that supports auth. Uncomment this with a valid username/password
"""
tg = TweetGen(BasicAuthOpener('USERNAME', 'PASSWORD'))
ret = json.load(tg.statuses_followers(screen_name=user))

print 'Mike has these followers:\n%s' % (
    ','.join(u['name'] for u in ret))
"""
