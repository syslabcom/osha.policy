from interfaces import IProviderHelper
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView
from AccessControl import getSecurityManager

class ProviderHelper(BrowserView):
    implements(IProviderHelper)

    def getMyProviders(self, obj):
        """ See interface """
        pUIDs = getattr(obj, 'getRemoteProviderUID', None)
        if not pUIDs:
            return list()
        if callable(pUIDs):
            pUIDs = pUIDs()
        sm = getSecurityManager()
        pc = getToolByName(self, 'portal_catalog')
        res = pc(UID = pUIDs)
        providers = list()
        for r in res:
            provider = r.getObject()
            if sm.checkPermission('View', provider):
                providers.append(provider)

        return providers
