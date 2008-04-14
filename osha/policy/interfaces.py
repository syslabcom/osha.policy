from zope.interface import Interface, alsoProvides
from plone.app.layout.navigation.interfaces import INavigationRoot


class ISubsite(Interface):
    """ A subsite which is identified by a keyword, can have its own skin, ...
    """
    
#alsoProvides(ISubsite, INavigationRoot)
    