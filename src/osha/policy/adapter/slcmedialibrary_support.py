from zope.interface import implements
from slc.treecategories.interfaces import IVocabularyInfo

class OSHAVocabularyInfo(object):
    implements(IVocabularyInfo)

    def __init__(self, *args, **kw):
        pass

    display_ids = True