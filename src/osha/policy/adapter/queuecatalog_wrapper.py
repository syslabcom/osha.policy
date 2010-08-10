from zope.interface import alsoProvides
from plone.indexer.wrapper import WrapperSpecification, IndexableObjectWrapper as IOW
from plone.indexer.interfaces import IIndexableObjectWrapper, IIndexableObject
from zope.interface import implements, providedBy, Interface
from Products.ZCatalog.interfaces import IZCatalog
from Products.CMFCore.utils import getToolByName
from Products.QueueCatalog.QueueCatalog import QueueCatalog
from zope.component import adapts, queryMultiAdapter

class IQueueCatalog(Interface):
    pass


class IndexableObjectWrapper(IOW):
    """A simple wrapper for indexable objects that will delegate to IIndexer
    adapters as appropriate.
    """
    
    implements(IIndexableObject, IIndexableObjectWrapper)
    adapts(Interface, IQueueCatalog)
    
#    __providedBy__ = WrapperSpecification()
    
    def __init__(self, object, catalog):
        super(IndexableObjectWrapper, self).__init__(object, catalog)
        self.__catalog = self.__catalog.getZCatalog()
