from interfaces import IVocabularyHelpers, ISEPHelpers, ISEPFolder
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView

class VocabularyHelpers(BrowserView):
    implements(IVocabularyHelpers)
    
    def getUIDsByTerms(self, termList=[], vocabularyName=''):
        """See interface"""
        print "getUIDsByTerms, termList:", termList
        pv = getToolByName(self, 'portal_vocabularies')
        catalog = getToolByName(self, 'portal_catalog')
        if type(termList) not in (list, tuple):
            termList = [termList]
        print "now termList is:", termList
        cat_uids = set()
        cat_str = ""
        if len(termList):
            VOCAB = getattr(pv, vocabularyName, None)
            if VOCAB:
                for term in termList:
                    if cat_str:
                        cat_str += "&"
                    cat_str += "%(name)s:list=%(term)s" % (dict(name=vocabularyName, term=term))
                    
                    try:
                        nelems = term.split("/")
                        nodePath = ""
                        for elem in nelems:
                            nodePath += "term.%s/" % elem
                        print "looking for node with path:", nodePath
                        node = VOCAB.restrictedTraverse(nodePath)
                        cat_uids.update(set(node.getTermKeyPath()))
                    except Exception, e:
                        print "Could not get Categories. Error: %s"%e
        return dict(cat_uids=list(cat_uids), cat_str=cat_str)

    def getHierarchyByName(self, vocabName):
        """See interface"""
        pass

class SEPHelpers(BrowserView):
    implements(ISEPHelpers)
    
    def getMySEP(self, context, REQUEST=None):
        """See interface"""
        if not REQUEST:
            REQUEST = context.REQUEST

        for obj in REQUEST.PARENTS:
            if ISEPFolder.providedBy(obj):
                return obj
        return None

    def getCategories(self, context):
        """See interface"""
        return context.getProperty('Category')
