# Default value for the publication products author field

from zope.interface import implements
from Products.Archetypes.interfaces import IFieldDefaultProvider
from slc.subsite.root import getSubsiteRoot
from Products.CMFCore.utils import getToolByName

class DefaultForPublicationAuthor(object):
    implements(IFieldDefaultProvider)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        subsite_root = getSubsiteRoot(self.context)

        if subsite_root.find("belgium") > 0:
            lang = getToolByName(self.context, 'portal_languages').getPreferredLanguage()
            if lang=='fr':
                return u"Service Public Fédéral Emploi, Travail et Concertation sociale"
            # nl is default
            else:
                return u"Federale Overheidsdienst Arbeid en Sociaal Overleg"

        return u"European Agency for Safety and Health at Work"
