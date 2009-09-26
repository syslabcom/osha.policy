from zope.component import adapts
from zope.interface import Interface, implements, alsoProvides, providedBy

from osha.policy.interfaces import ISingleEntryPoint


class SingleEntryPoint(object):
    """adapts an object to support being a SEP
    """
    implements(ISingleEntryPoint)
    