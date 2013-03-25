from slc.seminarportal.content.speaker import SPSpeaker
from Products.ATContentTypes.interfaces.topic import IATTopic
import gocept.linkchecker.interfaces
import gocept.linkchecker.utils
import zope.component
import zope.interface


class SPSpeakerRetriever(object):
    """Retriever for documents with one or more RichText widgets.

    SPSpeaker doesn't implement Products.Archetypes.atapi.BaseContent
    so the default ATGeneral retriever isn't registered for it."""

    zope.component.adapts(SPSpeaker)
    zope.interface.implements(gocept.linkchecker.interfaces.IRetriever)

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        return gocept.linkchecker.utils.retrieveAllRichTextFields(self.context)

    def updateLink(self, oldurl, newurl):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        gocept.linkchecker.utils.updateAllRichTextFields(
            oldurl, newurl, self.context)


class TopicRetriever(object):
    """Retriever for documents with one or more RichText widgets.

    ATTopic doesn't implement Products.Archetypes.atapi.BaseContent
    so the default ATGeneral retriever isn't registered for it."""

    zope.component.adapts(IATTopic)
    zope.interface.implements(gocept.linkchecker.interfaces.IRetriever)

    def __init__(self, context):
        self.context = context

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        return gocept.linkchecker.utils.retrieveAllRichTextFields(self.context)

    def updateLink(self, oldurl, newurl):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        gocept.linkchecker.utils.updateAllRichTextFields(
            oldurl, newurl, self.context)
