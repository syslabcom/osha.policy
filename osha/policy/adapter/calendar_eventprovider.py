from zope import interface
from zope import component
from p4a.calendar import interfaces
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.ATContentTypes.content import topic
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from p4a.plonecalendar.eventprovider import _make_zcatalog_query, ATEventProvider as BASEATEventProvider, TopicEventProvider as BASETopicEventProvider

class ATEventProvider(BASEATEventProvider):
    interface.implements(interfaces.IEventProvider)
    component.adapts(atapi.BaseObject)

    def __init__(self, context):
        self.context = context

    def gather_events(self, start=None, stop=None, **kw):
        
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()

        # search in the navigation root of the currently selected language and in the canonical path
        # with Language = preferredLanguage or neutral
        paths = list()
        portal_state = getMultiAdapter((self.context, self.context.request), name=u'plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()
        paths.append(navigation_root_path)
        try:
            navigation_root = portal_state.portal().restrictedTraverse(navigation_root_path)
            canonical_path = '/'.join(navigation_root.getCanonical().getPhysicalPath())
            paths.append(canonical_path)
        except:
            pass

        kw.update(dict(path=paths, Language=['', preflang]))
        kw = _make_zcatalog_query(start, stop, kw)
        event_brains = catalog(portal_type='Event', **kw)
        return (interfaces.IEvent(x) for x in event_brains)


    # Not needed at the moment
#class TopicEventProvider(BASETopicEventProvider):
#    interface.implements(interfaces.IEventProvider)
#    component.adapts(topic.ATTopic)
#
#    def __init__(self, context):
#        self.context = context
#        
#    def gather_events(self, start=None, stop=None, **kw):
#        print "custom gather_events of TopicEventProvider"
#        kw = _make_zcatalog_query(start, stop, kw)
#
#        # This sad hack allows us to overwrite whatever restriction
#        # the topic makes to the date.  Providing the 'start' and
#        # 'date' arguments to the 'queryCatalog' method would
#        # otherwise just overwrite our own date criteria.
#        # See http://plone4artists.org/products/plone4artistscalendar/issues/35
#        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
#        def my_catalog(request, **kwargs):
#            kwargs.update(kw)
#            return catalog(request, **kwargs)
#        self.context.portal_catalog = my_catalog
#        self.context.portal_catalog.searchResults = my_catalog
#        value = (interfaces.IEvent(x) for x in self.context.queryCatalog())
#        del self.context.portal_catalog
#        return value