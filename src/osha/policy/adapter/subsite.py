from zope.component import adapts
from zope.interface import Interface, implements, alsoProvides, providedBy

from osha.policy.interfaces import ISubsite


class Subsite(object):
    """adapts an object to support being a subsite
    """
    implements(ISubsite)
    