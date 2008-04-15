from zope.interface import Interface, alsoProvides
from plone.app.layout.navigation.interfaces import INavigationRoot


class ISubsite(INavigationRoot):
    """ A subsite which can have its own skin and navigation
    """
    
class ISingleEntryPoint(Interface):
    """ A SEP which is identified by a keyword, can have its own skin, ...
    """    

    