from interfaces import INaceView, ITopicView
from Products.CMFCore.utils import getToolByName
from Products.AdvancedQuery import Eq, Generic, In

from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView

class NaceView(BrowserView):
    implements(INaceView)
    
    def resultsOverview(self, cat_uids=[],alphabetical=False):
        """See interface"""
        nacelist=list()
        pv = getToolByName(self, 'portal_vocabularies')
        catalog = getToolByName(self, 'portal_catalog')

        mi_ids = catalog.uniqueValuesFor('osha_NACE')
        mi_ids = [x for x in mi_ids if x is not None and x!='']

        # get all objects with current site_position that have a NACE entry
        try:
            query = In('Category' , cat_uids) \
                & Generic('osha_NACE',mi_ids)
#                & Eq('review_state', 'published') 
            print "query:", query
            results = catalog.evalAdvancedQuery(query)

        except Exception, e:
            print "err: %s" %e
            kw = dict(osha_NACE= mi_ids)
            if len(cat_uids):
                kw['Category'] = cat_uids
            results = catalog(kw)
        print "have results", len(results)

        # make a mapping that holds the number of entries for each NACE code
        nacecount = {}
        for res in results:
            valpath = res.getOSHA_NACE
            for val in valpath:
    #            if val[0]=='/':
    #                val = val[1:]
                if nacecount.has_key(val):
                    nacecount[val] = nacecount[val] +1
                else:
                    nacecount[val] = 1

        VOCAB_NACE = pv.NACE
        # make a list that holds Title, id and counter for each NACE code
        for id in mi_ids:
            if nacecount.has_key(id):
                path = 'term.nace/term.%s'%str(id[1:])
                mynode = VOCAB_NACE.restrictedTraverse(path)
                title = mynode.Title()
                nacelist.append(dict(counter = nacecount[id], 
                                id = id, 
                                Title=title))

        if alphabetical:
            nacelist.sort(lambda x, y: cmp(x['Title'].lower(), y['Title'].lower()))
        else: 
            nacelist.sort(lambda x, y: cmp(x['id'], y['id']))

        # add the cat_uids, so they do not have to be looked up again on the details page
        
        return nacelist 



    def resultsByNACE(self, nace='', cat_uids=[]):
        """See interface"""
        catalog = getToolByName(self, 'portal_catalog')

        kw = {'osha_NACE': nace, 'Category' : cat_uids}
        results = catalog(kw)
        # make a real list out of the LazyMap
        results = list(results)
        # sort alphabetically
        results.sort(lambda x, y: cmp(x.Title.lower(), y.Title.lower()))
        return results


class TopicView(BrowserView):
    implements(ITopicView)

    def resultsOverview(self, context, cat_uid=''):
        """See interface"""
        toplist = list()
        pv = getToolByName(self, 'portal_vocabularies')
        catalog = getToolByName(self, 'portal_catalog')
        uid_catalog = getToolByName(self, 'uid_catalog')

        mi_ids = catalog.uniqueValuesFor('osha_Country')
        mi_ids = [x for x in mi_ids if x is not None and x!='']

#        VOCAB_Categories = pv.Categories
#        nelems = Category.split("/")
#        nodePath = ""
#        for elem in nelems:
#            nodePath += "term.%s/" % elem
#        term = VOCAB_Categories.restrictedTraverse(nodePath)
        catRes = uid_catalog(UID=cat_uid)
        if len(catRes):
            term = catRes[0].getObject()
        else:
            return toplist
        vocabDict = term.getVocabularyDict(context)
        for termkey in vocabDict.keys():
            try:
                query = In('Category' , termkey) 
#                & Eq('review_state', 'published')
    
                results = catalog.evalAdvancedQuery(query)
            except Exception, e:
                print "error in AdvancedQuery: %s"%e
                results = catalog(Category=termkey)
            if len(results):
                toplist.append(dict(counter=len(results),
                                Title=vocabDict[termkey][0],
                                cat_uid=termkey))

        return toplist

    def getResultsByCategory(self, cat_uid='', byCountry=False):
        """See interface"""
        catalog = getToolByName(self, 'portal_catalog')
        country_map = dict()
        try:
            query = In('Category', cat_uid)
            results = catalog.evalAdvancedQuery(query)
        except Exception,e:
            print "err in advanced Q: %s"%e
            kw = {'Category' : cat_uid}
            results = catalog(kw)
        # make a real list out of the LazyMap
        results = list(results)
        for r in results:
            valpath = r.getOSHA_Country
            if valpath is None: continue
            for val in valpath:
                if country_map.has_key(val):
                    country_map[val] = country_map[val] +1
                else:
                    country_map[val] = 1 
        print "\n country_map:", country_map
        # sort alphabetically
        results.sort(lambda x, y: cmp(x.Title.lower(), y.Title.lower()))
        return results
