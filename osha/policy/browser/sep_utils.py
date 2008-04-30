import Acquisition, StringIO
from interfaces import IVocabularyHelpers, ISEPHelpers, ISEPFolder
from Products.CMFCore.utils import getToolByName

from zope.interface import implements, Interface
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
