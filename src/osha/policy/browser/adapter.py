from zope.component import adapts
from zope.interface import Interface, implements, alsoProvides, providedBy

from interfaces import ISEPFolder


class SEPFolder(object):
    """adapts an object to support our metadata storage
    """
    implements(ISEPFolder)
    adapts(ISEPFolder)