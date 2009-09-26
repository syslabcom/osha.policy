# Default value for the publication products author field

from zope.interface import implements
from Products.Archetypes.interfaces import IFieldDefaultProvider

class DefaultForPublicationAuthor(object):
    implements(IFieldDefaultProvider)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        return u"European Agency for Safety and Health at Work"