from types import *
import Acquisition, StringIO
from interfaces import IVocabularyHelpers, ISEPHelpers, ISEPFolder
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, Interface
from Products.CMFPlone import utils
from Products.Five import BrowserView

# # Maps Nace code 1 to Nace code 2 taking 2 digits into account
NACE_MAP = {
'5': '3',
'10': '5',
'11': '6',
'12': '8',
'13': '7',
'14': '8',
'15': ('10','11'),
'16': '12',
'17': '13',
'18': '14',
'19': '15',
'20': '16',
'21': '17',
'22': '18',
'23': '19',
'24': '20',
'25': '22',
'26': '23',
'27': '24',
'28': '25',
'29': '28',
'30': '26',
'31': '27',
'32': '26',
'33': '26',
'34': '29',
'35': '30',
'36': '31',
'37': '38',
'40': '38',
'41': ('36', '38', '37'),
'45': '41',
'50': '45',
'51': '46',
'52': '47',
'55': ('55', '56'),
'60': '49',
'61': '50',
'62': '51',
'63': '52',
'64': ('53', '61'),
'65': '64',
'66': '65',
'67': '66',
'70': '68',
'71': '77',
'72': '62',
'73': '72',
'74': ('69', '70', '71', '73', '74', '75', '78', '79', '80', '81', '82', '95'),
'75': '84',
'80': '85',
'85': ('86', '87', '88'),
'90': ('37', '38', '39'),
'91': '94',
'92': ('58', '59', '60', '63', '90', '91', '93'),
'93': '96',
'95': '97',
'99': '99'
}


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


class IMigrateNaceCodes(Interface):
    pass

class MigrateNaceCodes(BrowserView):
    implements(IMigrateNaceCodes)

    def __call__(self):
        reindex = not not self.request.get('reindex', False)
        limit = self.request.get('limit', 0)
        limit = int(limit)
        out = StringIO.StringIO()
        out.write("Converting the Nace codes\n")
        out.write("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n")
        out.write("\n\n")
        if limit >0:
            out.write("Limiting to %s objects\n" %limit)
        else:
            out.write("No limit. Convert all objects\n")
            
        context = Acquisition.aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        results = portal_catalog.searchResults(Language='all')
        cnt = 0
        for brain in results:
            try:
                ob = brain.getObject()
            except AttributeError:
                continue
            o,n = self.rewriteNaceCodes(ob, reindex)
            if o is not None:
                cnt +=1
                out.write("Path: %s\nOld: %s\nNew: %s\n\n" % (brain.getPath(), o,n))

            if limit >=0 and cnt >=limit:
                break

        out.write("%s objects done" % cnt)
        return out.getvalue()        


    def rewriteNaceCodes(self, ob, reindex=0):
        if hasattr(Acquisition.aq_base(ob), '__nace_migrated__'):
            return None, None
        if not hasattr(Acquisition.aq_base(ob), 'getField'):
            return None, None
        field = ob.getField('nace')
        if field is None:
            return None, None
        oldnace = field.getAccessor(ob)()
        if len(oldnace)==0:
            return None, None
        # should be a tuple or list
        ob.__oldnace__ = oldnace
        if type(oldnace) in [ListType, TupleType]:
            oldnace = list(oldnace)
        elif type(oldnace) in [StringType, UnicodeType]:
            oldnace = [oldnace]
        else:
            raise TypeError, "oldnace is not list nor string!! %s is %s" %(oldnace, type(oldnace))
        
        newnace = set()
        for code in oldnace:
            subst = NACE_MAP.get(code, code)
            if type(subst) in [TupleType, ListType]:
                newnace = newnace.union(subst)
            else:
                newnace.add(subst)
        newnace = tuple(newnace)
        field.getMutator(ob)(newnace)
        ob.__newnace__ = newnace
        ob.__nace_migrated__ = True
        if reindex==1:
            ob.reindexObject('nace')
        return oldnace, newnace
    

class ITopicDirectory(Interface):
    pass
    
class TopicDirectory(BrowserView):
    implements(ITopicDirectory)
    #template = ViewPageTemplateFile('admin_feedback.pt')
    
    def __call__(self):
        self.request.set('disable_border', True)
        out = StringIO.StringIO()
        out.write("Adding the Topic Directory Structure to analyse site content\n")
        out.write("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n")
        out.write("\n\n")
        context = Acquisition.aq_inner(self.context)
        portal_catalog = getToolByName(context, 'portal_catalog')
        portal_types = getToolByName(context, 'portal_types')
        portal_properties = getToolByName(context, 'portal_properties')

        def _cisort(a,b):
            return cmp(a.lower(), b.lower())
            
        subjects = list(portal_catalog.uniqueValuesFor('Subject'))
        subjects.sort(_cisort)
        out.write("Subjects: %s\n\n" % ", ".join(subjects))

        types = list(portal_types.objectIds())
        types.sort(_cisort)
        out.write("Types: %s\n\n" %", ".join(types))
        
        typesNotToSearch = list(portal_properties.site_properties.getProperty('types_not_searched'))
        typesNotToSearch.sort(_cisort)
        out.write("TypesNotSearch: %s\n\n" %", ".join(typesNotToSearch))
        
        mytypes = [x for x in types if x not in typesNotToSearch]   
        mytypes.append('Subsite')
        mytypes.append('Publication')    
        mytypes.sort(_cisort) 
        out.write("Mytypes %s\n\n" % ", ".join(mytypes))
        
        id = "directory"
        if id not in context.objectIds():
            context.invokeFactory("Folder", id)
        D = getattr(context, id)
        D.setTitle("Topic Directory")
        D.setExcludeFromNav(True)
        D.reindexObject()
        
        for subject in subjects:
            if subject not in D.objectIds():
                D.invokeFactory('Topic', subject)

            ob = getattr(D, subject)
            ob.setTitle("All Items on %s" % subject)
            ob.setDescription('All Items tagged with the subject %s' % subject)
            ob.setText('')
            ob.setLayout('atct_topic_view')
            #if portal_workflow.getInfoFor(ob, 'review_state') in ('visible'):
            #    portal_workflow.doActionFor(ob, 'publish')
            
            if not 'crit__Subject_ATSimpleStringCriterion' in ob.objectIds():
                path_crit = ob.addCriterion('Subject', 'ATSimpleStringCriterion')      
                path_crit.setValue(subject)
        
            if not 'crit__effective_ATSortCriterion' in ob.objectIds():
                sort_crit = ob.addCriterion('effective', 'ATSortCriterion')
                sort_crit.setReversed(True)
            ob.reindexObject()
            out.write("Added Topic on %s\n" % subject)

            for T in mytypes:
                if T not in ob.objectIds():
                    ob.invokeFactory('Topic', T)
    
                sob = getattr(ob, T)
                sob.setTitle("All %s-Items on %s" % (T, subject))
                sob.setDescription('All %s-Items tagged with the subject %s' % (T, subject))
                sob.setText('')
                sob.setAcquireCriteria(True)
                sob.setLayout('atct_topic_view')

                if T == 'Publication':
                    if not 'crit__object_provides_ATListCriterion' in sob.objectIds():
                        portaltype_crit = sob.addCriterion('object_provides', 'ATListCriterion')
                        portaltype_crit.setValue('slc.publications.interfaces.IPublicationEnhanced')                               
                elif T == 'Subsite':
                    if not 'crit__object_provides_ATListCriterion' in sob.objectIds():
                        portaltype_crit = sob.addCriterion('object_provides', 'ATListCriterion')
                        portaltype_crit.setValue('slc.subsite.interfaces.ISubsiteEnhanced')            
                    
                else:                
                    if not 'crit__Subject_ATSimpleStringCriterion' in sob.objectIds():
                        path_crit = sob.addCriterion('portal_type', 'ATSimpleStringCriterion')      
                        path_crit.setValue(T)
            
                if not 'crit__effective_ATSortCriterion' in sob.objectIds():
                    sort_crit = sob.addCriterion('effective', 'ATSortCriterion')
                    sort_crit.setReversed(True)
    
                sob.reindexObject()
                out.write("Added Topic on %s and portal_type %s\n" % (subject, T))
                

        out.write("Done")                                      
        return out.getvalue()
        
    #return self.template() 
