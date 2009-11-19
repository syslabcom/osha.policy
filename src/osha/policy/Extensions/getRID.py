from Products.CMFCore.utils import getToolByName

def getRID(self):
    """ return catalog RID """
    #import pdb; pdb.set_trace()
    pc = getToolByName(self, 'portal_catalog')
    cat = getattr(pc, '_catalog', None)
    if not cat:
        return "Error, could not access the _catalog attribute of the portal_catalog"
    path = '/'.join(self.getPhysicalPath())
    return cat.getrid(path)
    