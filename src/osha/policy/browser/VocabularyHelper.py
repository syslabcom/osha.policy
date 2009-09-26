from interfaces import IVocabularyHelper
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView
from Products.Archetypes.utils import DisplayList


class VocabularyHelper(BrowserView):
    implements(IVocabularyHelper)


    def getDisplayListFor(self, vocabularyName=''):
        """See interface"""
        pv = getToolByName(self, 'portal_vocabularies')
        VOCAB = getattr(pv, vocabularyName, None)
        if not VOCAB:
            return DisplayList()
        DL = VOCAB.getDisplayList(self)
        return DL

    def getCountryList(self):
        """See interface"""
        result = DisplayList()
        pv = getToolByName(self, 'portal_vocabularies')
        VOCAB = getattr(pv, 'Country', None)
        if not VOCAB:
            return result
        vd = VOCAB.getVocabularyDict(self)
        
        for k in vd.keys():
            result.add('_%s' %k, '-- %s --'% vd[k][0])
            for r in vd[k][1].keys():
                result.add(r, vd[k][1][r][0])
        return result


    def getNaceList(self):
        """See interface"""
        result = DisplayList()
        pv = getToolByName(self, 'portal_vocabularies')
        VOCAB = getattr(pv, 'NACE', None)
        if not VOCAB:
            return result
        vd = VOCAB.getVocabularyDict(self)
        result = DisplayList()
        for k in vd.keys():
            result.add(k, vd[k][0])
        return result

    def getSubjectList(self):
        """See interface"""
        pc = getToolByName(self, 'portal_catalog')
        vals = pc.uniqueValuesFor('Subject')
        result = DisplayList()
        for v in vals:
            result.add(v,v)
        return result