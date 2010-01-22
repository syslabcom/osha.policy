from zope.app.component.interfaces import ISite

from five.localsitemanager import make_objectmanager_site
            
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

from Products.ATContentTypes.interface import IATEvent
from Products.ATContentTypes.interface import IATNewsItem
from Products.ATContentTypes.interface import IATDocument
from Products.PressRoom.interfaces.content import IPressRelease
from Products.CMFCore.utils import getToolByName

from osha.adaptation.schema import OshaMetadataExtender
from zope.interface.declarations import noLongerProvides

def run(self, path=''):
    result = list()
    result.append('setOshaMetadataExtension')
    url_tool = getToolByName(self, 'portal_url')
    portal = url_tool.getPortalObject()
    obj = self
    if path:
        try:
            obj = portal.restrictedTraverse(path)
        except:
            result.append("No object found for path %s" %path)
            return "\n".join(result)

    # very special and dirty hack
    # We need to kill the existing SiteManager in the European Riskobservatory
    # folder, since it contains a reference to the no longer existing
    # IEroExtender
    if obj.id in ['riskobservatory', ] and ISite.providedBy(obj):
        noLongerProvides(obj, ISite)
        del obj._components
        result.append('Deleted existing site manager')

    if not ISite.providedBy(obj):
        make_objectmanager_site(obj)
        result.append("Turned %s into a local site" %obj.id)

    sitemanager = obj.getSiteManager()
    sitemanager.registerAdapter(
                            OshaMetadataExtender,
                            (IATEvent,),
                            IOrderableSchemaExtender,
                            name='event-oshametadata',
                            )

    sitemanager.registerAdapter(
                            OshaMetadataExtender,
                            (IATNewsItem,),
                            IOrderableSchemaExtender,
                            name='news-oshametadata',
                            )

    sitemanager.registerAdapter(
                            OshaMetadataExtender,
                            (IATDocument,),
                            IOrderableSchemaExtender,
                            name='document-oshametadata',
                            )

    sitemanager.registerAdapter(
                            OshaMetadataExtender,
                            (IPressRelease,),
                            IOrderableSchemaExtender,
                            name='pressrelease-oshametadata',
                            )

    result.append("Registered OshaMetadataExtender as adapter on %s" %obj.id)

    return "\n".join(result)


