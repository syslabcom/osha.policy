# Reason for this completely sick-in-the-brain patch:
# https://dev.plone.org/plone/ticket/10088
# http://groups.google.com/group/plone-users/browse_thread/thread/78ed22c2bac39a68

# I cannot seem to say
# Archetypes.utils.isFactoryContained = MyisFactoryContained
# since the patch is not picked up that way

# Therefore I patched CatalogMultiplex.CatalogMultiplex.unindexObject,
# where the exception occurs.

# I also had to modify the handling of __url()
# In the original unindexObject(), the line reads:
# url = self.__url(),
# which seems to work, even though in pdb I get:
# self.__url / self.__url()
# *** AttributeError: __url
# While this seems to work in the original method (afterwards, the variable url
# does indeed contain the url), it breaks in the patch. Therefore the
# diference in code, but not in function for __url


#from Products import  Archetypes 
from Products.Archetypes import CatalogMultiplex #import CatalogMultiplex


def __url(self):
    return '/'.join( self.getPhysicalPath() )


def MyisFactoryContained(obj):
    """Are we inside the portal_factory?
    """
    pobj = obj.aq_inner.aq_parent
    return hasattr(pobj, 'meta_type') and pobj.meta_type == 'TempFolder'

#Archetypes.utils.isFactoryContained = MyisFactoryContained

def unindexObject(self):
    if MyisFactoryContained(self):
        return
    catalogs = self.getCatalogs()
    url = __url(self)
    for c in catalogs:
        if c._catalog.uids.get(url, None) is not None:
            c.uncatalog_object(url)

CatalogMultiplex.CatalogMultiplex.unindexObject = unindexObject
