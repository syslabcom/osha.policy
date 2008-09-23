from Products.CMFCore.utils import getToolByName
from slc.subsite import isSubsite
from Acquisition import aq_parent
from Products.PloneLanguageTool.LanguageTool import LanguageTool

def setDefaultLanguage(self, langCode):
    """Sets the default language."""
#    import pdb; pdb.set_trace()
    if isSubsite(aq_parent(self)):
        oshaview = self.restrictedTraverse('@@oshaview')
        return oshaview.set_subsite_property('default_language', langCode)
    portal_properties = getToolByName(self, "portal_properties")
    site_properties = portal_properties.site_properties
    if site_properties.hasProperty('default_language'):
        return site_properties._updateProperty('default_language', langCode)
    portal = getUtility(ISiteRoot)
    if portal.hasProperty('default_language'):
        return portal._updateProperty('default_language', langCode)
    self.default_lang = langCode

LanguageTool.setDefaultLanguage = setDefaultLanguage

def getDefaultLanguage(self):
    """Returns the default language."""
#    import pdb; pdb.set_trace()
    if isSubsite(aq_parent(self)):
        oshaview = self.restrictedTraverse('@@oshaview')
        return oshaview.get_subsite_property('default_language')
    portal_properties = getToolByName(self, "portal_properties", None)
    if portal_properties is None:
        return 'en'
    site_properties = portal_properties.site_properties
    if site_properties.hasProperty('default_language'):
        return site_properties.getProperty('default_language')
    portal = getUtility(ISiteRoot)
    if portal.hasProperty('default_language'):
        return portal.getProperty('default_language')
    return getattr(self, 'default_lang', 'en')

LanguageTool.getDefaultLanguage = getDefaultLanguage
