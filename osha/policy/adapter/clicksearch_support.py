from zope.interface import Interface, implements, alsoProvides
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from slc.clicksearch.interfaces import ISelectView
from slc.clicksearch.util import *
from slc.clicksearch.browser.widgets import BaseView, SimpleListView


class MultilingualThesaurusView(SimpleListView):
    """ creates a view for the Multilingual Thesaurus metadatum """
    template = ViewPageTemplateFile('clicksearch_multilingualthesaurus.pt')
    template_selected = ViewPageTemplateFile('clicksearch_multilingualthesaurus_selected.pt')

    def __call__(self, index, top=[]):     
        self.index = index
        self.top = top
        vtool = getToolByName(self.context, 'portal_vocabularies')
        vocab = getattr(vtool, 'MultilingualThesaurus')
        self.manager = vocab._getManager()

        if index in self.request.keys():
            return self.template_selected()

        return self.template()
    
    def selected_value_caption(self):
        return self.manager.getTermCaptionById(self.request.get(self.index))
            
    def children(self):
        term = self.selected_value()
        term_node = self.manager.getTermById(term)
        terms = self.manager.getTerms(term_node)
        children = []
        query = current_query(self.request)
        for key in terms.keys():
            query['multilingual_thesaurus'] = key
            new_qs = make_qs(query)
            children.append(dict(id=key, title=terms[key][0], link="clicksearch?%s" % new_qs))
        return children
        
    