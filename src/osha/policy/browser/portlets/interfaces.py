from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface, Attribute
from plone.portlets.interfaces import IPortletManager

class ISEPPublicationsPortlet(Interface):
    """Interface for portlet to display related publications"""

    def results():
        """Get the list of related publications"""

class IRelatedByTypePortlet(Interface):
    """Interface for portlet to display related content by type"""

    def results():
        """Get the list of related content by type"""
        
        
