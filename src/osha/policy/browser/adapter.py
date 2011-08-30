from zope.component import adapts
from zope.interface import Interface, implements, alsoProvides, providedBy

from interfaces import ISEPFolder


class SEPFolder(object):
    """adapts an object to support our metadata storage
    """
    implements(ISEPFolder)
    adapts(ISEPFolder)


def handleToggleOutdated(event):
    """If an object was marked as outdated, remove it from the linkchecker
    (unregister). If the outdated flag was removed, register it again. """
    pass
    # To be done once we have plone.app.async in place

