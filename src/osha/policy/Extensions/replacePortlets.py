import Acquisition
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from zope.component.interfaces import ComponentLookupError
from slc.googlesearch.portlets import searchbox
from slc.googlesearch.browser.settings import AvailableCSEVocabularyFactory
from plone.app.portlets.browser.editmanager import ManagePortletAssignments
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from plone.app.portlets.utils import assignment_mapping_from_key
from zope.exceptions.interfaces import DuplicationError
from StringIO import StringIO
import transaction
import logging

logger = logging.getLogger('osha.policy.replacePortlets')

def replaceSearchPortlets(self):
    """Recursively replace 'search' portlets with 'google-searchbox' """""
    portal = self.portal_url.getPortalObject()
    ltool = getToolByName(portal, 'portal_languages')
    langs = ltool.getSupportedLanguages()
    #langs = ['en']
    
    vocab = AvailableCSEVocabularyFactory(self)
    self.cse = len(vocab._terms) and vocab._terms[0].value or ''
    self.out = StringIO()
    self.out.write('Starting with replacement of the "search" portlet.\n\n')

    # copied from plone.app.portlets
    def move_portlet_up(assignments, name):
        keys = list(assignments.keys())
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)


    def doReplacement(self, obj):
        #print "handling", obj.absolute_url()
        path = '/'.join(obj.getPhysicalPath())
        try:
            right = assignment_mapping_from_key(obj, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
        except ComponentLookupError:
            #print "no portlets possible for", obj
            return
        portlets = [x for x in list(right.keys())]
        
        new_name = 'google-searchbox'
        if 'search' in portlets:
            # import pdb; pdb.set_trace()
            index = portlets.index('search')
            print "replacing portlets on ", obj
            del right['search']
            if new_name in portlets:
                return
            right[new_name] = searchbox.Assignment(selected_CSE=self.cse)

            keys =  list(right.keys())
            google_index = keys.index(new_name)
            while google_index!=index:
                move_portlet_up(right, new_name)
                keys =  list(right.keys())
                google_index = keys.index(new_name)
            print [x for x in list(right.keys())]
            self.out.write('Did replacement on %s\n' %path)

    def doRecursion(self, obj):
        for subobj in obj.objectValues():
            doReplacement(self, subobj)
            if IFolderish.providedBy(subobj):
                doRecursion(self, subobj)
      
    for lang in langs:
        if not hasattr(Acquisition.aq_base(portal), lang):
            self.out.write("\nNo folder '%s' found on portal, skipping\n" %lang)
            continue
        self.out.write("\nHandling language '%s'\n" %lang)
        F = getattr(portal, lang)
        doReplacement(self, F)
        doRecursion(self, F)
        
    return self.out.getvalue()


def removeSearchPortlets(self):
    """Recursively replace 'search' portlets with 'google-searchbox' """""
    portal = self.portal_url.getPortalObject()
    ltool = getToolByName(portal, 'portal_languages')
    langs = ltool.getSupportedLanguages()
    self.out = StringIO()
    self.out.write('Starting with replacement of the "search" portlet.\n\n')

    def doReplacement(self, obj):
        #print "handling", obj.absolute_url()
        path = '/'.join(obj.getPhysicalPath())
        try:
            right = assignment_mapping_from_key(obj, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
        except ComponentLookupError:
            #print "no portlets possible for", obj
            return
        portlets = [x for x in list(right.keys())]
        
        name = 'google-searchbox'
        if name in portlets:
            # import pdb; pdb.set_trace()
            index = portlets.index(name)
            print "removing portlet on ", obj
            del right[name]
            self.out.write('Did replacement on %s\n' %path)

    def doRecursion(self, obj):
        for subobj in obj.objectValues():
            doReplacement(self, subobj)
            if IFolderish.providedBy(subobj):
                doRecursion(self, subobj)
      
    for lang in langs:
        if not hasattr(Acquisition.aq_base(portal), lang):
            self.out.write("\nNo folder '%s' found on portal, skipping\n" %lang)
            continue
        self.out.write("\nHandling language '%s'\n" %lang)
        F = getattr(portal, lang)
        doReplacement(self, F)
        doRecursion(self, F)
        transaction.commit()
        logger.warning('Commited for language %s' % lang)
        
    return self.out.getvalue()
