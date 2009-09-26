from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.interfaces import ITranslatable
from Acquisition import aq_parent, aq_inner
from Products.Archetypes.config import LANGUAGE_DEFAULT

# Reason for this patch:
# In subsites, we want to be able to add a local portal_languages tool.
# Upon content creation, the local tool must be asked about startNeutral

def defaultLanguage(self):
    """Returns the initial default language."""
    parent = aq_parent(aq_inner(self))
    if ITranslatable.providedBy(parent):
        language = parent.Language()
        if language:
            return parent.Language()

    oshaiew = self.restrictedTraverse('@@oshaview')
    site_url = oshaiew.subsiteRootPath()
    site = self.restrictedTraverse(site_url)
    language_tool = getToolByName(site, 'portal_languages', None)
    if language_tool:
        if language_tool.startNeutral():
            return ''
        else:
            return language_tool.getPreferredLanguage()
    else:
        return LANGUAGE_DEFAULT

I18NBaseObject.defaultLanguage = defaultLanguage
