from zope.app.component.interfaces import ISite
from five.localsitemanager import make_objectmanager_site
from Products.CMFCore.utils import getToolByName
from osha.policy.adapter.schemaextender import TaggingSchemaExtenderERO

def setEROSchemaExtension(self, path=''):
    result = list()
    url_tool = getToolByName(self, 'portal_url')
    portal = url_tool.getPortalObject()
    obj = None
    if path:
        try:
            obj = portal.restrictedTraverse(path)
        except:
            # well, path must habe been wrong
            result.append("No object found for path %s" %path)

    if not obj:
        obj = self
        result.append("Performing actions on self (%s)" %obj.absolute_url())

    if not ISite.providedBy(obj):
        make_objectmanager_site(obj)
        result.append("Turned %s into a local site" %obj.id)
    sitemanager = obj.getSiteManager()

    sitemanager.registerAdapter(factory=TaggingSchemaExtenderERO,
                                         name=u"osha.metadata.ero")

    result.append("Registered TaggingSchemaExtenderERO as adapter on %s" %obj.id)

    return "\n".join(result)
