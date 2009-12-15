from zope.app.component.interfaces import ISite

from five.localsitemanager import make_objectmanager_site
            
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

from Products.ATContentTypes.interface import IATEvent
from Products.CMFCore.utils import getToolByName
from Products.RALink.content.interfaces import IRALink
from Products.CaseStudy.interfaces import ICaseStudy

from osha.policy.adapter.schemaextender import LinkListExtender 

def run(self, path=''):
    result = list()
    url_tool = getToolByName(self, 'portal_url')
    portal = url_tool.getPortalObject()
    obj = None

    if path:
        try:
            obj = portal.restrictedTraverse(path)
        except:
            result.append("No object found for path %s" %path)
            return "\n".join(result)

    if not ISite.providedBy(obj):
        make_objectmanager_site(obj)
        result.append("Turned %s into a local site" %obj.id)

    sitemanager = obj.getSiteManager()
    sitemanager.registerAdapter(
                            LinkListExtender,
                            (IATEvent,),
                            IOrderableSchemaExtender,
                            )

    sitemanager.registerAdapter(
                            LinkListExtender,
                            (IRALink,),
                            IOrderableSchemaExtender,
                            )

    sitemanager.registerAdapter(
                            LinkListExtender,
                            (ICaseStudy,),
                            IOrderableSchemaExtender,
                            )

    result.append("Registered LinkListExtender as adapter on %s" %obj.id)

    return "\n".join(result)


