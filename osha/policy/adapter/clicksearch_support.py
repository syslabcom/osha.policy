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

        self.reverse_dict = self.create_reverse_term_dict()

        if index in self.request.keys():
            return self.template_selected()

        return self.template()
    
    def selected_value_caption(self):
        return self.manager.getTermCaptionById(self.request.get(self.index))
    
    def create_reverse_term_dict(self):
        """ create a dict which allows to resolve the parents"""
        vdict = self.manager.getVocabularyDict()
        reverse_dict = {}
        
            
        def register_parent(parent, dict):
            for k,v in dict.items():
                new_parent = k
                reverse_dict[k] = parent
                if v[1] is None:
                    continue
                register_parent(new_parent, v[1])
                
        register_parent(None, vdict)
        
        return reverse_dict
        
    def get_parents(self):
        """ returns a list of captions for all parents of the given term """
        parentlist = []
        X = self.selected_value()
        query = current_query(self.request)
        while True:
            X = self.reverse_dict.get(X)
            if X is None:
                break
            caption = self.manager.getTermCaptionById(X)
            query['multilingual_thesaurus'] = X
            new_qs = make_qs(query)
            parentlist.append(dict(id=X, title=caption, link="clicksearch?%s" % new_qs))
        parentlist.reverse()
        return parentlist
        
    def children(self):
        children = []
        term = self.selected_value()
        term_node = self.manager.getTermById(term)
        terms = self.manager.getTerms(term_node)
        if terms is None:
            return children
        query = current_query(self.request)
        for key in terms.keys():
            query['multilingual_thesaurus'] = key
            new_qs = make_qs(query)
            children.append(dict(id=key, title=terms[key][0], link="clicksearch?%s" % new_qs))
        return children

    