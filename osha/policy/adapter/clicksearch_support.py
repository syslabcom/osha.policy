from zope.interface import Interface, implements, alsoProvides
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from slc.clicksearch.interfaces import ISelectView
from slc.clicksearch.util import *
from slc.clicksearch.browser.widgets import BaseView, SimpleListView, ATVMTreeListView
from slc.clicksearch.browser.indexes import DefaultIndexView, ATVMTreeIndexView


class CountryView(SimpleListView):
    """ creates a view for the Country metadatum """
    #template = ViewPageTemplateFile('clicksearch_country.pt')
    #template_selected = ViewPageTemplateFile('clicksearch_country_selected.pt')


class SubcategoryView(ATVMTreeListView):
    """ creates a view for the Subcategory metadatum """
    #template = ViewPageTemplateFile('clicksearch_subcategory.pt')
    #template_selected = ViewPageTemplateFile('clicksearch_subcategory_selected.pt')
    vocabulary_name = "Subcategory"



class SubcategoryIndexView(ATVMTreeIndexView):
    #template = ViewPageTemplateFile('subcategory_index.pt')
    vocabulary_name = "Subcategory"


class MultilingualThesaurusView(ATVMTreeListView):
    """ creates a view for the Multilingual Thesaurus metadatum """
    #template = ViewPageTemplateFile('clicksearch_multilingualthesaurus.pt')
    #template_selected = ViewPageTemplateFile('clicksearch_multilingualthesaurus_selected.pt')
    vocabulary_name = "MultilingualThesaurus"

class MultilingualThesaurusIndexView(ATVMTreeIndexView):
    #template = ViewPageTemplateFile('subcategory_index.pt')
    vocabulary_name = "MultilingualThesaurus"



