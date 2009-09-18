from Acquisition import aq_inner, aq_parent
from Products.AdvancedQuery import In, Eq, Ge, Le, And, Or, Generic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from osha.theme.browser.dbfilter import DBFilterView

class PracticalSolutionsView(DBFilterView):
    """ View Class for the Practical Solutions page. 

        Provides a link to each section based on the folder title.
        If there is an image called "section-image.png" in the folder
        it will be used too.
        """
    template = ViewPageTemplateFile('templates/practical_solutions.pt')
    template.id = "practical-solutions"

    gpawards = ''
    intro = ''
    has_section_details = False
    sections = ['useful-links',
                'risk-assessment-tools',
                'case-studies',
                'providers',
                'faqs']

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

    def search_portal_types(self):
        context = self.context
        search_portal_types = [ "OSH_Link", "RALink", "CaseStudy", "Provider"]
        query = ( Eq('portal_type', 'File') & Eq('object_provides', 'slc.publications.interfaces.IPublicationEnhanced') )
        query = Or(query, In('portal_type', search_portal_types)) & Eq('review_state','published')
        return query

    def getSectionDetails(self):
        """ Return a path to an image and a title for each of the five Practical 
            Solutions sections.
            """
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


class PracticalSolutionView(DBFilterView):
    """View for displaying one of the practical solution sections.

    The section heading, image and search parameters (portal_type) are derived
    from the parent folder.

    The Title of the parent folder is used as a caption under the image for the
    current section (to be consistent with the PracticalSolutionsView).
    If there is an image in that folder called 'section-image.png' it will be
    used too. 
    The portal-type to search for is derived from the id of the parent
    folder.
    """

    template = ViewPageTemplateFile('templates/practical_solution.pt')
    template.id = "practical-solution"

    portal_types_map = {
            "useful-links":"OSH_Link",
            "risk-assessment-tools":"RALink",
            "case-studies":"CaseStudy",
            "providers":"Provider",
            "faqs":"Publication",
            }
    
     
    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()

    def has_section_image(self):
        """ Check if an image called section-image.png exists in the folder """
        context = self.context
        parent = aq_parent(aq_inner(context)) 
        return "section-image.png" in parent.objectIds()

    def getSectionTitle(self):
        """ Return the title of the parent folder """
        context = self.context
        parent = aq_parent(aq_inner(context)) 
        return parent.Title()

    def search_portal_types(self):
        context = self.context
        parent = aq_parent(aq_inner(context)) 
        search_portal_types = []
        if self.portal_types_map.has_key(parent.id):
            search_portal_types = [self.portal_types_map[parent.id]]

        query = None
        if 'Publication' in search_portal_types:
            query = ( Eq('portal_type', 'File') & Eq('object_provides', 'slc.publications.interfaces.IPublicationEnhanced') )
            search_portal_types.remove('Publication')
            query = Or(query, In('portal_type', search_portal_types))
        else:
            query = In('portal_type', search_portal_types)
        query = query & Eq('review_state','published')

        return query


