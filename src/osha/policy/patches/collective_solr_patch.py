from collective.solr import indexer
from collective.solr.indexer import datehandler

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
