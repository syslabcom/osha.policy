from Products.CMFCore.utils import getToolByName
from Products.Collage.browser.viewlet import ActionsViewlet

def getViewActions(self):

    atool = getToolByName(self.context, 'portal_actions')
    # This is the killer line that leads to an incredible loading time
    # on the compose page.
    # It is apparently NOT NEEDED!!
#    actions = atool.listFilteredActionsFor(self.context.aq_inner)
    plone_view = self.context.restrictedTraverse('@@plone')
    return plone_view.prepareObjectTabs()

ActionsViewlet.getViewActions = getViewActions