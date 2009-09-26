from cStringIO import StringIO
from Products.CMFCore.utils import getToolByName

def run(self):
    """Replace the catalog tool with portal_catalog_real.
       This is sometimes necessary when a 3rd party app breaks
       PloneQueueCatalog.
    """
    out = StringIO()
    old_cat = getToolByName(self, 'portal_catalog_real')

    setattr(portal, 'portal_catalog', old_cat)
    portal._delObject('portal_catalog_real')
    objmap = portal._objects
    for info in objmap:
        if info['id'] == 'portal_catalog':
            info['meta_type'] = old_cat.meta_type
    portal._objects = objmap
    out.write(' - Replaced QueueCatalog with Portal Catalog tool')
