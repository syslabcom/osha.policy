from zope import interface
from zope import component
from zope.component import getMultiAdapter

from Products.AdvancedQuery import In, And, Not, Eq, Ge, Le
from Products.CMFCore import utils as cmfutils
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName

from p4a.calendar import interfaces
from p4a.plonecalendar.eventprovider import _make_zcatalog_query
from p4a.plonecalendar.eventprovider import \
        ATEventProvider as BASEATEventProvider


class ATEventProvider(BASEATEventProvider):
    interface.implements(interfaces.IEventProvider)
    component.adapts(atapi.BaseObject)

    def __init__(self, context):
        self.context = context

    def gather_events(self, start=None, stop=None, **kw):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')

        # search in the navigation root of the currently selected language
        # and in the canonical root path with Language = preferredLanguage or
        # neutral
        pstate = getMultiAdapter((self.context, self.context.request),
                        name=u'plone_portal_state')

        nav_root_path = pstate.navigation_root_path()
        paths = [nav_root_path]

        nav_root = pstate.portal().restrictedTraverse(nav_root_path)
        try:
            canonical_path = '/'.join(
                nav_root.getCanonical().getPhysicalPath())
        except AttributeError:
            pass
        else:
            if canonical_path not in paths:
                paths.append(canonical_path)

        portal_languages = getToolByName(self.context, 'portal_languages')
        preflang = portal_languages.getPreferredLanguage()

        # If we are in the root (i. e. not inside a subsite), restrict
        # to the current folder. This restores the p4a.calendar's behaviour of
        # gather_events, since that also returns only events from the current
        # calendar.
        oshaview = getMultiAdapter((self.context, self.context.request),
                    name=u'oshaview')
        subsite = oshaview.getCurrentSubsite()

        if subsite is None:
            paths = ['/'.join(self.context.getPhysicalPath())]

        query = And(
            Eq('portal_type', 'Event'),
            In('path', paths),
            In('Language', ['', preflang]),
            )

        # Not sure where this key comes from, but it is not an index...
        if '-C' in kw:
            del kw['-C']

        kw = _make_zcatalog_query(start, stop, kw)
        for key, value in kw.items():
            if key in ['start', 'end']:
                if value['range'] == 'max':
                    query = And(query, Le(key, value['query']))
                else:
                    query = And(query, Ge(key, value['query']))
            else:
                query = And(query, Eq(key, value))

        if hasattr(catalog, 'getZCatalog'):
            catalog = catalog.getZCatalog()

        event_brains = catalog.evalAdvancedQuery(query, (('Date', 'desc'),))
        return (interfaces.IEvent(x) for x in event_brains)
