from Products.CMFCore.utils import getToolByName
from Products.Collage.browser.viewlet import ActionsViewlet

def getViewActions(self):

    # Instead of calling plone_view.prepareObjectTabs() on every single
    # item in the Collage for information we don't need anyway, we simply
    # return two views: edit and view, which is enough for our case
    url = self.context.absolute_url()
    actions = [
        dict(id='view', selected=False, title=u'View', url=url),
        dict(id='edit', selected=False, title=u'Edit', url=url + '/edit'),
    ]
    return actions

ActionsViewlet.getViewActions = getViewActions