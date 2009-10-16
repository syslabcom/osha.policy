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
            return u"parliament_question_author"

        return u"European Agency for Safety and Health at Work"
