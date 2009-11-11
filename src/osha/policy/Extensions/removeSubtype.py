from zope import component
from p4a.subtyper.interfaces import ISubtyper
from Products.CMFCore.utils import getToolByName
from p4a.image.interfaces import IImageEnhanced

def removeSubtype(self):
    """ no modularity whatsoever at the moment """
    cat = getToolByName(self, 'portal_catalog')
    res = cat(portal_type='Image', Language='all', object_provides='p4a.image.interfaces.IImageEnhanced')

    subtyperUtil = component.getUtility(ISubtyper)
    status = list()
    status.append("we have %d images" %len(res))
    for r in res:
        ob = r.getObject()
        if not ob:
            continue
        if IImageEnhanced.providedBy(ob):
            if subtyperUtil.existing_type(ob) is not None:
                subtyperUtil.remove_type(ob)
                ob.reindexObject()
                status.append('Removed subtype on %s' %ob.absolute_url())
            else:
                status.append("ERROR: got an image that provides IImageEnhanced but ain't subtyped! %s" % ob.absolute_url() )
    print "game over"
    return "\n".join(status)