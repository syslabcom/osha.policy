from Products.kupu.plone.plonedrawers import PloneDrawers
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

# We want the subsite root to be used for the "Home" link, not the general portal root

def getBreadCrumbs(self, context, template):
    """Return breadcrumbs for drawer"""
    resource_type = self.getResourceType()
    if not resource_type.allow_browse:
        return []
        
    oshaview = getMultiAdapter((context, context.REQUEST), name='oshaview')
    id = template.getId()
    putils = getToolByName(self, 'plone_utils')
    lutils = getToolByName(context, 'portal_languages')
    path = [ ("Home", oshaview.subsiteRootUrl()+'?set_language=%s'%lutils.getPreferredLanguage())]

    if getattr(putils.aq_base, 'createBreadCrumbs', None) is not None:
        path = path + [(x['Title'],x['absolute_url']) for x in putils.createBreadCrumbs(context)]
    else:
        path = path + self.breadcrumbs(context)[1:-1]

    # Last crumb should not be linked:
    path[-1] = (path[-1][0], None)

    crumbs = []
    for title,url in path:
        if url:
            url = self.kupuUrl("%s/%s" % (url.rstrip('/'), id))
        crumbs.append({'Title':title, 'absolute_url':url})

    return crumbs

PloneDrawers.getBreadCrumbs = getBreadCrumbs