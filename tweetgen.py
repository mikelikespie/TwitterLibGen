from data import methods

import urllib2
import urllib

class NeedAuthException(Exception): pass

class BaseOpener(object):
    """
    Use this class without instantiating it if you
    want to use library without auth
    """

    authorize = False
    
    @staticmethod
    def post(url, data):
        return urllib2.urlopen(url, urllib.urlencode(data))

    @staticmethod
    def get(url, data):
        return urllib2.urlopen("%s?%s" % (url, urllib.urlencode(data)))

    @staticmethod
    def delete(url, data):
        raise NotImplementedError()


class BasicAuthOpener(object):
    """
    Use this class if you have authorization

    You must instantiate it
    """

    authorize = True

    def __init__(self, username, password):
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(realm='Twitter API',
                                  uri='http://twitter.com',
                                  user=username,
                                  passwd=password)
        self.opener = urllib2.build_opener(auth_handler)

    def post(self, url, data):
        return self.opener.open(url, urllib.urlencode(data))

    def get(self, url, data):
        return self.opener.open("%s?%s" % (url, urllib.urlencode(data)))

    def delete(self, url, data):
        raise NotImplementedError()



#TODO: Add oauth opener here



def validate(params, valid_methods, args, kwargs):
    """
    validates the params and the required params
    returns all args with args, and required merged
    """
    def make_prototype(required_params, optional_params):
        return ", ".join(required_params + ["%s=None" % p for p in optional_params])



    optional_params = [v['name'] for v in params if not v['required']]
    required_params = [v['name'] for v in params if v['required']]
    # let's do some validation

    #sanitize Nones out of kwargs
    kwargs = dict((k,v) for k,v in kwargs.iteritems() if v is not None)

    if len(args) + len(kwargs) > len(optional_params) + len(required_params):
        raise ValueError("Too many arguments. Got %s. Requires <= %s.\nParams are (%s)" %
                (len(args) + len(kwargs),
                 len(optional_params) + len(required_params),
                 make_prototype(required_params, optional_params)))

    #zip together the args in the order we got the list
    new_args = dict(zip(required_params + optional_params, args))

    overlapping_args = set(new_args.keys()).intersection(set(kwargs.keys()))

    if len(overlapping_args) > 0:
        #if we have more than one definition of the same argument
        raise ValueError("Recieved %s arguments twice.\nParams are (%s)" %
            (",".join(list(overlapping_args)), make_prototype(required_params, optional_params)))

    #now that we have the right number of args, let's merge kwargs and args
    new_args.update(kwargs)

    required_missing = set(required_params)-set(kwargs.keys())
    if len(required_missing) > 0:
        raise ValueError("We're missing (%s) arguments" % ",".join(list(required_missing)))

    #probably don't need to do this, but this is just a prototype
    param_dict = dict((p['name'], p) for p in params)
    for k,v in kwargs.iteritems():
        if k in param_dict:
            p = param_dict[k]
            if 'type' in p:
                type = p['type']
                if type == 'int':
                    if not isinstance(v, int):
                        raise ValueError("Parameter %s must be an int" % k)
                    if 'min' in p:
                        if v < p['min']:
                            raise ValueError("Minimum value for %s is %s" % (k, p['min']))
                    if 'max' in p:
                        if v > p['max']:
                            raise ValueError("Maximum value for %s is %s" % (k, p['max']))

        elif k != 'method': #yeah we want to ignore method
            raise ValueError("%s is not valid parameter.\n Possible parameters include (%s)" %
                            (k, make_prototype(required_params, optional_params)))


    if 'method' in new_args:
        method = new_args['method']
        if method not in valid_methods:
            raise ValueError("%s is not a valid method. valid ones are (%s)" %
                    (method, ','.join(md['methods'])))

    return new_args



def genmethod(md):
    name = md['name']

    valid_methods = md['methods']
    main_method = valid_methods[0]
    params = md['parameters']
    requires_auth = md['requires_auth']

    def func(self, *args,**kwargs):
        all_args = validate(params,
                            valid_methods,
                            args, kwargs)
        
        method = main_method
        if 'method' in all_args:
            method = all_args['method']
            del(all_args['method'])
        
        if requires_auth is True:
            if not self.opener.authorize:
                raise NeedAuthException(
                        "%s requires authorization and %s does not support it" % 
                            (name, str(self.opener)))

        return self.dispatch(method, name, all_args)
    
    normal_name = name.replace('/', '_')

    func.__name__ = normal_name

    return normal_name, func

all_methods = tuple(m['name'].replace('/', '_') for m in methods)

class TweetGen(object):
    __slots__ = all_methods + ('opener', '__init__', 'base_url', 'dispatch')
    base_url = 'http://twitter.com/'
    def __init__(self, opener):
        self.opener = opener

    def dispatch(self, method, url, data):
        method = method.upper()
        url += '.json'
        if method == 'GET':
            return self.opener.get(self.base_url + url, data)
        elif method == 'POST':
            return self.opener.post(self.base_url + url, data)
        elif method == 'DELETE':
            return self.opener.delete(self.base_url + url, data)
        else:
            raise ValueError("method '%s' not supported" % method)


for m in methods:
    setattr(TweetGen, *genmethod(m))

