from interfaces import IRelatedByTypePortlet
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_base

from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView


class RelatedByTypePortlet(BrowserView):
    implements(IRelatedByTypePortlet)

    def results(self, portal_type=None):
        """ """
        if hasattr(aq_base(self), 'context'):
            context = self.context
        else:
            context = self
        portal_catalog = getToolByName(context, 'portal_catalog')
        typesToShow = portal_type
        results = self.request.get(
            'items',
            portal_catalog.searchResults(sort_on='modified',
                                         portal_type=typesToShow,
                                         sort_order='reverse',
                                         sort_limit=5))
        return results[0:min(5, len(results))]

            