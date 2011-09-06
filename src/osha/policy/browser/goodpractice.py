from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

class GoodPracticeView(BrowserView):
    """View for displaying the dynamic good practice overview page at /good_practice
       This view will be replace with PracticalSolutionsView
    """
    gpawards = ''
    intro = ''

    sections = ['useful-links',
                'risk-assessment-tools',
                'case-studies',
                'providers',
                'faqs']

    has_section_details = False

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

        return self.index()

    def getSectionDetails(self):
        """ Return a path to an image and a title for each of the five Practical 
            Solutions sections if they exists"""
        context = self.context
        section_details = {}

        for section in self.sections:
            if section in context.objectIds():
                section_details[section] = {}
                # The title is taken from the local version
                section_details[section]["title"] = context[section].Title()
                canonical_section = context.getCanonical()[section]
                # The image is taken from the canonical version
                if "section-image.png" in canonical_section.objectIds():
                    section_details[section]["section_image_src"] = \
                        canonical_section["section-image.png"].absolute_url()
                self.has_section_details = True
        return section_details

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
            title = ttool.getTypeInfo(typ[0]).Title()
            if title.endswith('y'):
                title = title[:-1] + "ies"
            else:
                title = title + "s"
            type_name = _(title)
            typelist.append(dict(caption=type_name, id=typ, url=url))

        return typelist
