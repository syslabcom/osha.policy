from interfaces import ISEPPublicationsPortlet
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView

class SEPPublicationsPortlet(BrowserView):
    implements(ISEPPublicationsPortlet)

    def results(self):
        """ """
        context = utils.context(self)
        putils = getToolByName(context, 'plone_utils')
        portal_catalog = getToolByName(context, 'portal_catalog')
        typesToShow = ['Publication']
        return self.request.get(
            'items',
            portal_catalog.searchResults(sort_on='modified',
                                         portal_type=typesToShow,
                                         sort_order='reverse',
                                         sort_limit=5)[:5])
