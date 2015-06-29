from __future__ import with_statement
import sys, optparse, re, string, copy, operator, random, logging, os, decorator, base64, threading, math, htmlentitydefs, unicodedata, urllib, hashlib, shelve, cPickle

import simplejson as json

from itertools import *
from functools import *
from collections import defaultdict

def importNamespace(globals, ns, ignorehidden=True):
    """import all keys from namespace ns into the globals (globals())"""
    globals.update((key, getattr(ns, key)) for key in dir(ns)
                                            if not ignorehidden or not key.startswith('_'))

class Struct(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    #FIXME: __unicode__
    def __str__(self):
        return "".join("%s: %s\n" % (key, repr(getattr(self, key))) \
                                        for key in dir(self) \
                                                if not key.startswith('_') \
                                                and not callable(getattr(self, key)))

class JStruct(Struct, dict):
    """object that behaves like javascript -- access either via attributes or items"""
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr)
    def __setattr__(self, attr, val):
        self[attr] = val
    def __str__(self):
        return "".join("%s: %s\n" % (key, value) for key, value in self.items()\
                        if not key.startswith('__') and not callable(value))
    def __hash__(self):
        self.__id__ = getattr(self, '__id__', random.randrange(1<<32))
        return self.__id__

def recFlatten(iterable):
    """recursively flatten all iterables"""
    if not hasattr(iterable, "__iter__"):
        yield iterable
        return
    for item in iterable:
        for val in recFlatten(item):
            yield val

def flatten(iterable):
    """flatten iterable, one level"""
    for items in iterable:
        for item in items:
            yield item

def bSearch(items, val):
    """binary search on sorted list items"""
    idx = bisect.bisect(items, val)
    return idx > 0 and items[idx-1] == val

#FIXME: document
def cumulDict(reduceop, default_factory):
    class CumulDict(defaultdict):
        def __init__(self, seq=None):
            defaultdict.__init__(self, default_factory)
            if seq:
                self.update(seq)

        #FIXME: make the behavior compatible with regular dict.update;
        #allow dict as input in addition to pairs
        def update(self, seq):
            for k, v in seq:
                self[k] = reduceop(self[k], v)

    return CumulDict

def summarize(seq, key, value, reduceop, default_factory):
    return cumulDict(reduceop, default_factory)(((key(v), value(v)) for v in seq))

histDict = partial( summarize,
                                        key=lambda x: x,
                                        value=lambda x: x,
                                        reduceop=lambda x, y: x+1,
                                        default_factory=lambda: 0)
SumDict = cumulDict(lambda x, y: x + y, lambda: 0)
ConcatDict = cumulDict(lambda x, y: x + [y], lambda: [])
CollectDict = cumulDict(lambda x, y: x | set([y]), lambda: set())
#clever version. bad.
MapDict = cumulDict(lambda d, (k, v): d.__setitem__(k, v) or d, dict)

#FIXME: rewrite in terms of histDict
def getHist(values, mincount=0, topn=None):
    """returns dict representing a dictogram of a list of values
    only returns keys that appear at least mincount times
    only returns topn most frequent keys, all if topn is None"""
    hist = {}
    def add(v):
        try: hist[v] += 1
        except: hist[v] = 1
    #FIXME: remove this behavior!
    for v in values:
        if isinstance(v, list): map(add, v)
        else: add(v)
    for key in copy.copy(hist):
        if hist[key] < mincount:
            del hist[key]
    if topn is not None:
        hist = dict(sorted(hist.items(), key = lambda (k, v): -v)[:topn])
    return hist

def getMultiDict(sequence):
    dic = {}
    for k, v in sequence:
        try: dic[k].append(v)
        except: dic[k] = [v]
    return dic

class EasyParser(optparse.OptionParser):

    def __init__(self, opts=""):

        def guessType(string):
            if string == "None": return None, "string"
            try: return int(string), "int"
            except: pass
            try: return float(string), "float"
            except: pass
            return string, "string"

        optparse.OptionParser.__init__(self)

        for opt in opts.split():
            key, spam, value, colon = re.compile("([^=]*)(=([^:]*))?(:)?").search(opt).groups() #example: "key=value:"
            if value is not None: default, deftype = guessType(value)
            action = "store" if colon else "store_true"
            kwargs = {"action": action}
            if value is not None: kwargs["default"] = default
            if value is not None and colon: kwargs["type"] = deftype
            try:
                self.add_option(*["-" + key[0], "--" + key], **kwargs)
            except optparse.OptionConflictError:
                self.add_option("--" + key, **kwargs)

class Sampler:
    def __init__(self, items, weightFunc = lambda spam:1.0):
        """items is either a dict or a list
        if it is a dict, keys are sampled from and values are treated as the p.d.f."""

        #convert p.d.f. to dict
        if isinstance(items, dict):
            weights = self.weights = items
        else:
            weights = self.weights = dict((item, weightFunc(item)) for item in items)

        #normalize
        totalweight = float(sum(weights.itervalues()))
        assert totalweight > 0
        for k in weights:
            weights[k] /= totalweight #weights guaranteed floats from now on

        #split into bins
        maxwt = max(weights.itervalues())
        itemsbybin = {}
        numbins = 64
        binspread = 2.0
        for item in items:
            if weights[item] <= maxwt / binspread ** numbins:
                continue
            bin = int(math.log(maxwt / weights[item], binspread))
            itemsbybin.setdefault(bin, []).append(item)
        itemlist = (itemsbybin[k] for k in xrange(numbins + 1) if k in itemsbybin)
        def makeBin(items):
            return {        'items': items,
                                    'totalweight': sum(map(weights.__getitem__, items)),
                                    'maxweight': max(map(weights.__getitem__, items))}
        self.bins = map(makeBin, itemlist)
        self.items = set(flatten(bin['items'] for bin in self.bins))

    def sample(self):
        r = random.random()
        partialsum = 0
        for bin in self.bins:
            partialsum += bin['totalweight']
            if partialsum > r:
                break
        for cnt in count():
            item = random.choice(bin['items'])
            if random.random() < self.weights[item] / bin['maxweight']:
                return item
            assert cnt < 100 #expected constant time, this should be exponentially rare

    def sampleWoR(self, size, exclude=set(), maxtries=None):
        """if maxtries is a positive integer, we will abort after that many
        tries and return the samples that we have.

        the number of samples returned may be may be smaller than size"""
        #FIXME: don't require maxtries, make algorithm cleverer
        if len(set(self.items) - exclude) <= size:
            return self.items
        samples = set()
        tries = xrange(maxtries) if maxtries else count()
        for spam in tries:
            sample = self.sample()
            if sample not in exclude:
                samples.add(sample)
            if len(samples) >= size:
                break
        return samples

#FIXME: should return list instead of set
def sampleWoR(items, size):
    """sample size items from a list of items"""
    if not hasattr(items, '__len__'):
        items = list(items)

    if len(items) <= size:
        return set(items)

    if len(items) < size * 2:
        return set(items) - sampleWoR(items, len(items)-size)

    samples = set()
    while len(samples) < size:
        samples.add(random.choice(items))
    return samples

#FIXME: replace by random.shuffle
def permute(items):
    permuted = list(items)
    for i in xrange(1, len(permuted)):
        j = random.randrange(i+1)
        permuted[i], permuted[j] = permuted[j], permuted[i]
    return permuted

def arithMean(iterable):
    sum, count = 0.0, 0
    for val in iterable:
        sum += val
        count += 1
    return sum / count

def getMedian(iterable, meanoftwo=False):
    """
    if meanoftwo is True for even sized lists the mean of the middle two elements
    will be returned. items need to support +
    """
    items = list(iterable)
    size = len(items)
    if size % 2 or not meanoftwo:
        return sorted(items)[size/2]
    smaller, bigger = sorted(items)[size/2-1:size/2+1]
    return (smaller + bigger) / 2

def getVariance(iterable):
    sum, sum2, count = 0.0, 0.0, 0
    for val in iterable:
        sum2 += val * val
        sum += val
        count += 1
    return sum2 / count  - (sum / count) ** 2

#FIXME
mean = arithMean
median = getMedian
variance = getVariance

def stdDev(iterable):
    try: return getVariance(iterable) ** 0.5
    except: return 0

def cosineSim(ldic, rdic, default=0):
    """cosine similarity of two vectors represented as dicts"""
    if not hasattr(ldic, 'iteritems'):
        ldic = dict((k, 1) for k in ldic)
    if not hasattr(rdic, 'iteritems'):
        rdic = dict((k, 1) for k in rdic)
    def norm(dic):
        return sum(v ** 2 for v in dic.itervalues()) ** 0.5
    common = set(ldic) & set(rdic)
    if len(common) == 0:
        return 0
    lnorm, rnorm = norm(ldic), norm(rdic)
    if lnorm * rnorm == 0:
        return default
    return sum(ldic[k] * rdic[k] for k in common) / lnorm / rnorm

def iirSmooth(sequence, decay):
    """decay is roughly the reciprocal of window"""
    outval, prevval = None, None
    for val in sequence:
        if outval is None: outval = val
        if prevval is not None:
            outval = val * decay + prevval * (1-decay)
        prevval = outval
        yield outval

def crossProduct2(iter1, iter2):
    for item1 in iter1:
        for item2 in iter2:
            yield item1, item2

#FIXME: replace by itertools.product
def crossProduct(*iters):
    if len(iters) == 2:
        for tuple in crossProduct2(*iters):
            yield tuple
    else:
        for item in iters[0]:
            for tuple in crossProduct(*iters[1:]):
                yield (item,) + tuple

def filterDupes(elems, keyfunc=lambda x:x):
    """filters dupes from a stream with the same value of keyfunc"""
    seenkeys = set()
    for elem in elems:
        key = keyfunc(elem)
        if key not in seenkeys:
            yield elem
            seenkeys.add(key)



def _tree_filter(node, filter_func):
    if filter_func(node):
        yield node
    for child in node.childNodes:
        for cn in tree_filter(child, filter_func):
            yield cn

def getElementById(node, id):
    """built in function requires you to parse DTD. idiotic."""
    def filter_func(node):
        try: return node.attributes['id'].value == id
        except: return False
    return _tree_filter(node, filter_func).next()

def getElementsByTagAndClassName(node, tag, cls=None):
    def filter_func(node):
        try: return not cls or node.attributes['class'].value == cls
        except: return False
    return filter(filter_func, node.getElementsByTagName(tag))

def getElementsByXPath(node, path):
    """because the libraries can go fuck themselves"""
    def getElementsByTagList(node, taglist):
        #same as outer fn. except path is represented as list
        if len(taglist) == 0:
            yield node
            return
        for child in node.getElementsByTagName(taglist[0]):
            for desc in getElementsByTagList(child, taglist[1:]):
                yield desc
    return getElementsByTagList(node, path.split("/"))

#FIXME: not needed anymore
def replace_entities(match, errors='ignore'):
    try:
        ent = match.group(1)
        if ent[0] == "#":
            if ent[1] == 'x' or ent[1] == 'X':
                return unichr(int(ent[2:], 16))
            else:
                return unichr(int(ent[1:], 10))
        return unichr(name2codepoint[ent])
    except:
        return  {
                                'copy'  : match.group(),
                                'ignore': ''
                        }[errors]


_entity_re = re.compile(r'&(#?[A-Za-z0-9]+?);')
def unescapeEntities(data):
    return _entity_re.sub(replace_entities, data)

#NOTE: not a dict. order is important.
_html_unescape_table = [
        ('"', "&quot;"),
        ("'", "&apos;"),
        (">", "&gt;"),
        ("<", "&lt;"),
        ("&", "&amp;"),
]

def unescapeHtml(string):
    """turn &amp; to &, etc."""
    for (k, v) in _html_unescape_table:
        string = string.replace(v, k)
    return unescapeEntities(string)

def stripAccents(unistr):
    nkfd_form = unicodedata.normalize('NFKD', unistr)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

_punctuation = string.punctuation + u"\u2013"
_trans_table = dict.fromkeys(map(ord, _punctuation), u' ')

def stripPunctuation(unistr):
    return unistr.translate(_trans_table)

def encodeUrl(prefix, kwargs):
    """takes a prefix and a dict of args and returns an encoded url
    sorts args in alphabetical order of keys. this helps with caching."""
    return prefix + '?' + '&'.join( '%s=%s' % (k, urllib.quote(kwargs[k].encode('utf-8')))
                                                                    for k in sorted(kwargs.keys()))


def hexNonce(size=16):
    """16 char random hex string, 64 bits of randomness
            (assuming random.randrange is random)"""
    return ("0"*size + "%x"%random.randrange(1<<64))[-size:]

def base64Nonce(size=12):
    b256size = (size+11 - ((size-1) % 12)) * 3/4
    nonce = "".join(chr(random.randrange(256)) for spam in xrange(b256size))
    return base64.urlsafe_b64encode(nonce)[-size:]

def base64Digest(text, size=12):
    hash = hashlib.sha1(text).digest()
    return base64.urlsafe_b64encode(hash)[:size]

def writeFile(filename, s):
    """dump string s to filename"""
    out = open(filename, 'w')
    out.write(s)
    out.close()


def getLogger(filename, loggername=None, loglevel=logging.DEBUG):
    logger = logging.getLogger(loggername)
    if len(logger.handlers) > 0: #already done init
        return logger
    handler = logging.FileHandler(filename)
    handler.setFormatter(logging.Formatter(\
            '%%(asctime)s    %%(levelname)s  pid:%d  %%(message)s' % os.getpid()))
    handler.setLevel(loglevel)
    logger.setLevel(loglevel)
    logger.addHandler(handler)
    logger.info('INIT')
    return logger

@decorator.decorator
def materialize(func, *args):
    return list(func(*args))

def failSilently(default=None, exception=Exception, logger=logging.getLogger()):
    @decorator.decorator
    def _wrapper(func, *args):
        try:
            return func(*args)
        except exception, error:
            try:
                argstr = ", ".join(map(str, args))
            except:
                argstr = None
            if argstr is not None and logger is not None:
                logger.debug("FAIL      %s(%s) [%s]" % (func.func_code.co_name, \
                        argstr if argstr  else '', error))
            return default
    return _wrapper

def getattrdefault(obj, attr, default_thunk):
    """similar to .setdefault in dictionaries.
    http://www.phyast.pitt.edu/~micheles/python/documentation.html#id10"""
    try:
        return getattr(obj, attr)
    except AttributeError:
        default = default_thunk()
        setattr(obj, attr, default)
        return default

def locked(lock=None):
    if not lock:
        lock = threading.Lock()
    @decorator.decorator
    def _locked(func, *args, **kwargs):
        with lock:
            return func(*args, **kwargs)
    return _locked

@decorator.decorator
def autoPack(func, *args):
    """turns a variable argument list into a single argument, a list
    if there is only one argument, leaves it alone
    useful for functions like max() which take either a single arg which is a list
    or a list of args"""
    if len(args) == 0:
        return func([])
    if len(args) == 1:
        return func(args[0])
    return func(args)

def cached(maxsize=1000000, keyfunc=None):
    @decorator.decorator
    def _cached(func, *args, **kwargs):
        cache = getattrdefault(func, "cache", dict)
        if len(cache) >= maxsize:
            for key in cache.keys():
                if random.randrange(5) == 0:
                    del cache[key]
        if keyfunc:
            key = keyfunc(args, kwargs)
        else:
            key = args, frozenset(kwargs.iteritems())
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return _cached

class ShelfWrapper():
    """a shelf helper class that supports key serialization
    not a subclass of shelf; supports only a limited interface

    this is hideous.  if we can be sure to catch all the entry points, then we can
    serialize/deserialize all of them. but we can't. so we can only provide limited
    functionality because we can't subclass
    """
    def __init__(self, *args, **kwargs):
        self.shelf = shelve.open(*args, **kwargs)

    def __getitem__(self, key):
        return self.shelf[self.serialize(key)]

    def __contains__(self, key):
        return self.serialize(key) in self.shelf

    def get(self, key, default=None):
        return self[key] if key in self else default

    def __setitem__(self, key, val):
        self.shelf[self.serialize(key)] = val

    def __delitem__(self, k):
        del self.shelf[self.serialize(k)]

    def __iter__(self):
        return (self.deserialize(kstr) for kstr in self.shelf)

    def __len__(self):
        return len(self.shelf)

    def serialize(self, k):
        return cPickle.dumps(k, cPickle.HIGHEST_PROTOCOL)

    def deserialize(self, kstr):
        return cPickle.loads(kstr)

    def close(self):
        self.shelf.close()

try:
    from mod_python import apache
    have_modpy = True
except:
    have_modpy = False

#TODO: decorator to treat arg as file or stream or string
def modpyApiWrite(req, obj):
    """sets content/type as well as writes output"""
    #if req is None then we are being called in a non-web context
    #so just return the obj, which is the answer
    if not req:
        return obj
    req.headers_out['Pragma'] = 'no-cache'
    req.headers_out['Cache-Control'] = 'no-cache'
    req.headers_out['Expires'] = '-1'
    req.content_type = "text/plain; charset=UTF-8"
    req.write(json.dumps(obj, indent=2))
    return None

def modpyHandler(func, *args, **kwargs):
    def newf(req, *args, **kwargs):
        if not hasattr(req, 'headers_out'):
            args = (req,) + args
            return func(*args, **kwargs)
        return modpyApiWrite(req, func(*args, **kwargs))
    return update_wrapper(newf, func) if have_modpy else func
