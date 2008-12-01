from zope.interface import Interface, implements, alsoProvides
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter

from slc.clicksearch.interfaces import ISelectView
from slc.clicksearch.util import *
from slc.clicksearch.browser.widgets import BaseView, SimpleListView, ATVMTreeListView
from slc.clicksearch.browser.indexes import DefaultIndexView, ATVMTreeIndexView


class RemoteLanguageView(SimpleListView):
    """ creates a view for the RemoteLanguage metadatum """

    def prepare_title(self, id):
        ltool = getToolByName(self.context, 'portal_languages')
        langs = ltool.getAvailableLanguageInformation()
        L = langs.get(id, None)
        if L is None:
            return id
        return L.get(u'native', L.get(u'name', id))
        
class CountryView(SimpleListView):
    """ creates a view for the Country metadatum """

    def prepare_title(self, id):
        ctool = getToolByName(self.context, 'portal_countryutils')
        isodict = ctool.getCountryIsoDict()
        
        return isodict.get(id, id)
        
        
class SubcategoryView(ATVMTreeListView):
    """ creates a view for the Subcategory metadatum """
    vocabulary_name = "Subcategory"

class SubcategoryIndexView(ATVMTreeIndexView):
    vocabulary_name = "Subcategory"


class NACEView(ATVMTreeListView):
    """ creates a view for the Subcategory metadatum """
    vocabulary_name = "NACE"

class NACEIndexView(ATVMTreeIndexView):
    vocabulary_name = "NACE"


class MultilingualThesaurusView(ATVMTreeListView):
    """ creates a view for the Multilingual Thesaurus metadatum """
    vocabulary_name = "MultilingualThesaurus"

class MultilingualThesaurusIndexView(ATVMTreeIndexView):
    vocabulary_name = "MultilingualThesaurus"



