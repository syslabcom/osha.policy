from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

class GoodPracticeView(BrowserView):
    """View for displaying the dynamic good practice overview page at /good_practice
    """
    template = ViewPageTemplateFile('goodpractice.pt')
    gpawards = ''
    intro = ''

    def __call__(self):
        self.request.set('disable_border', True)


        intro = getattr(self.context, 'introduction_html', None)
        if intro is None:
            self.intro = ''
        else:
            self.intro = intro.CookedBody()

        gpaward = getattr(self.context, 'good_practice_awards_html', None)
        if gpaward is None:
            self.gpaward = ''
        else:
            self.gpaward = gpaward.CookedBody()

        return self.template()

    def getAreaLinks(self, area=''):
        """ return the SEPS under topics """
        path = "/".join(self.context.getPhysicalPath())+'/' +area
        pc = getToolByName(self.context, 'portal_catalog')
        res = pc(path={'query': path, 'depth': 1}, portal_type="Folder", review_state='published', sort_on='sortable_title')
        return res


    def getLatestLink(self):
        """ Return latest link """
        pc = getToolByName(self.context, 'portal_catalog')
        res = pc(portal_type='OSH_Link', review_state='published', sort_on='effective', sort_order='reverse', limit=1)
        if len(res)==0:
            latestLink = None
        else:
            latestLink = res[0].getObject()


        return latestLink

    def anon(self):
        return getToolByName(self.context, 'portal_membership').isAnonymousUser()

    def get_db_types(self):
        """ return a list of object types with links to point to the clicksearch interface """
        T = ['OSH_Link', 'RALink', 'CaseStudy', 'Provider', 'File']
        typelist = []
        ttool = getToolByName(self.context, 'portal_types')
        for typ in T:
            url = "%s/db/clicksearch?portal_type=%s" % (self.context.absolute_url(), typ)
            if typ=='File':
                type_name = _('Publication')
            else:
                type_name = _(ttool.getTypeInfo(typ).Title())
            typelist.append(dict(caption=type_name, id=typ, url=url))

        return typelist

    def get_search_types(self):
        """ return a list of object types with links to point to the clicksearch interface """
        T = [('OSH_Link', 'index_oshlink'), ('RALink', 'index_ralink'), ('CaseStudy', 'index_casestudy'), ('Provider', 'index_provider')]
        typelist = []
        ttool = getToolByName(self.context, 'portal_types')
        for typ in T:
            url = "%s/%s" % (self.context.absolute_url(), typ[1])
            type_name = _(ttool.getTypeInfo(typ[0]).Title())
            typelist.append(dict(caption=type_name, id=typ, url=url))

        return typelist
