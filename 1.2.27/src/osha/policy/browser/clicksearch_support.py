
from zope.component import getMultiAdapter
from zope.interface import Interface, implements, alsoProvides

from Products.ATCountryWidget.CountryTool import Country
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.clicksearch.interfaces import ISelectView
from slc.clicksearch.util import *
from slc.clicksearch.browser.widgets import BaseView
from slc.clicksearch.browser.widgets import SimpleListView
from slc.clicksearch.browser.widgets import ATVMTreeListView
from slc.clicksearch.browser.widgets import DropdownView
from slc.clicksearch.browser.indexes import DefaultIndexView, ATVMTreeIndexView


class RemoteLanguageView(DropdownView):
    """ creates a view for the RemoteLanguage metadatum """

    template = ViewPageTemplateFile('widgets/clicksearch_language.pt')
    template_selected = ViewPageTemplateFile('widgets/clicksearch_language.pt')

    def prepare_title(self, id):
        ltool = getToolByName(self.context, 'portal_languages')
        langs = ltool.getAvailableLanguageInformation()
        L = langs.get(id, None)
        if L is None:
            return id
        return L.get(u'native', L.get(u'name', id))

    def index_values(self):
        """Return the values from the index
        """
        cat = getToolByName(self.context, 'portal_catalog')
        idx = cat._catalog.getIndex(self.index)
        ls = []
        lutils = getToolByName(self.context, 'portal_languages')
        ldict = lutils.getAvailableLanguageInformation()
        for lc in idx.uniqueValues():
            lang = ldict.get(lc, None)
            if lang is None:
                continue
            ls.append(lang)
        return ls


class CountryView(DropdownView):
    """ creates a view for the Country metadatum """

    template = ViewPageTemplateFile('widgets/clicksearch_country.pt')
    template_selected = ViewPageTemplateFile('widgets/clicksearch_country.pt')

    def prepare_title(self, id):
        ctool = getToolByName(self.context, 'portal_countryutils')
        isodict = ctool.getCountryIsoDict()

        return isodict.get(id, id)

    def index_values(self):
        """Return the values from the index
        """
        cat = getToolByName(self.context, 'portal_catalog')
        idx = cat._catalog.getIndex(self.index)
        cs = []
        cutils = getToolByName(self.context, 'portal_countryutils')
        cdict = cutils.getCountryIsoDict()
        for cc in idx.uniqueValues():
            name = cdict.get(cc, cc)
            cs.append(Country(cc, name))
        return cs


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



