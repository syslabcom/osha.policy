from collective.solr.flare import PloneFlare
from collective.solr import indexer, mangler
from collective.solr.indexer import datehandler
from collective.solr.mangler import *

def getRID(self):
    """ Return a Resource Identifier, like a brain would do """
    return self.UID 

PloneFlare.getRID = getRID

PloneFlare._unrestrictedGetObject = PloneFlare.getObject

def inthandler(value):
    # solr would choke on None and throw a javalangNumberFormatException,
    # preventing the whole object from being indexed. Therefore raise an
    # AttributeError in this case.
    if value is None:
        raise AttributeError
    return value

indexer.handlers = {
    'solr.DateField': datehandler,
    'solr.TrieDateField': datehandler,
    'solr.IntField': inthandler,
    'solr.TrieIntField': inthandler,
}

def mangleQuery(keywords):
    """ translate / mangle query parameters to replace zope specifics
        with equivalent constructs for solr """
    extras = {}
    for key, value in keywords.items():
        if key.endswith('_usage'):          # convert old-style parameters
            category, spec = value.split(':', 1)
            extras[key[:-6]] = {category: spec}
            del keywords[key]
        elif isinstance(value, dict):       # unify dict parameters
            keywords[key] = value['query']
            del value['query']
            extras[key] = value
        elif hasattr(value, 'query'):     # unify object parameters
            keywords[key] = value.query
            extra = dict()
            for arg in query_args:
                arg_val = getattr(value, arg, None)
                if arg_val is not None:
                    extra[arg] = arg_val
            extras[key] = extra

    for key, value in keywords.items():
        args = extras.get(key, {})
        if key == 'path':
            path = keywords['parentPaths'] = value
            del keywords[key]
            if 'depth' in args:
                depth = int(args['depth'])
                if depth >= 0:
                    if not isinstance(value, (list, tuple)):
                        path = [path]
                    tmpl = '(+physicalDepth:[%d TO %d] AND +parentPaths:%s)'
                    params = keywords['parentPaths'] = set()
                    for p in path:
                        base = len(p.split('/'))
                        params.add(tmpl % (base + 1, base + depth, p))
                del args['depth']
        elif key == 'effectiveRange':
            value = convert(value)
            del keywords[key]
            keywords['effective'] = '[* TO %s]' % value
            keywords['expires'] = '[%s TO *]' % value
        elif key == 'show_inactive':
            del keywords[key]           # marker for `effectiveRange`
        elif 'range' in args:
            if not isinstance(value, (list, tuple)):
                value = [value]
            payload = map(convert, value)
            keywords[key] = ranges[args['range']] % tuple(payload)
            del args['range']
        elif 'operator' in args:
            if isinstance(value, (list, tuple)) and len(value) > 1:
                sep = ' %s ' % args['operator'].upper()
                value = sep.join(map(str, map(convert, value)))
                keywords[key] = '(%s)' % value
            del args['operator']
        elif isinstance(value, basestring) and value.endswith('*'):
            keywords[key] = '%s' % value.lower()
        else:
            keywords[key] = convert(value)
        assert not args, 'unsupported usage: %r' % args

mangler.mangleQuery = mangleQuery
