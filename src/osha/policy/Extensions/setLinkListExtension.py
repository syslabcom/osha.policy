from zope.app.component.interfaces import ISite

from five.localsitemanager import make_objectmanager_site
            
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

from Products.ATContentTypes.interface import IATEvent
from Products.CMFCore.utils import getToolByName
from Products.RALink.content.interfaces import IRALink
from Products.CaseStudy.interfaces import ICaseStudy

from osha.adaptation.schema import LinkListExtender

def run(self, path=''):
    result = list()
    url_tool = getToolByName(self, 'portal_url')
    portal = url_tool.getPortalObject()
    obj = self
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
                            name='event-linklist',
                            )

    sitemanager.registerAdapter(
                            LinkListExtender,
                            (IRALink,),
                            IOrderableSchemaExtender,
                            name='ralink-linklist',
                            )

    sitemanager.registerAdapter(
                            LinkListExtender,
                            (ICaseStudy,),
                            IOrderableSchemaExtender,
                            name='casestudy-linklist',
                            )

    result.append("Registered LinkListExtender as adapter on %s" %obj.id)

    return "\n".join(result)


