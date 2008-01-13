from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.portlets.portlets import navigation

            
class PortalTitleViewlet(ViewletBase):
    render = ViewPageTemplateFile('portaltitle.pt')

    def update(self):
        pass

class SiteActionsViewlet(ViewletBase):
    render = ViewPageTemplateFile('site_actions.pt')

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        self.site_actions = context_state.actions().get('site_actions', None)

class TopBannerViewlet(ViewletBase):
    render = ViewPageTemplateFile('topbanner.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')

        self.navigation_root_url = portal_state.navigation_root_url()

        portal = portal_state.portal()
        topbannerName = 'topbanner.jpg'
        self.logo_tag = portal.restrictedTraverse(topbannerName).tag()

        self.portal_title = portal_state.portal_title()

                
class FooterViewlet(ViewletBase):
    render = ViewPageTemplateFile('oshafooter.pt')

    def update(self):
        pass            