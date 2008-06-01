from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from Products.OSHATranslations import OSHAMessageFactory as _

def helper(self):
    print "\nhelper"
    
    path = '/'.join(self.getPhysicalPath())
    
    portal = self.portal_url.getPortalObject()
    portal_path = self.portal_url.getPortalPath()
    langs = portal.portal_languages.getSupportedLanguages()
    
    right = assignment_mapping_from_key(self, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
    print right.keys()
    from plone.portlet.collection import collection as collection_portlet
    
    key = 'organisation'
    topic_path = "%s/directory/%s/Publication" %(portal_path, key)
    right[u'sep_publications'] = collection_portlet.Assignment(header=_(u"legend_publications"), 
                                   target_collection=topic_path, 
                                   limit=5)
    
    return "ok"


def LanguageSetter(self, lang=''):
    print "\n LanguageSetter"
    
    objs = self.objectValues()
    for obj in objs:
        obj._md['language'] = lang

    return "ok"