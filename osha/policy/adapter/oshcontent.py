# Add additional fields to the standard content types
# For now I assume that nearly all fields only are relevant for OSHContent
# except:
#   - Keywords, which will be handled by the plone subject
#   - html_meta_keywords, which are used to optimize the SEO Keywords
#   -


import zope.interface
class IOSHContent(zope.interface.Interface):
    """OSHContent
    """

from Products.Archetypes.utils import DisplayList

from Products.ATCountryWidget.Widget import CountryWidget, MultiCountryWidget

from Products.ATContentTypes.content import document
from Products.OSHContentLink.OSH_Link import OSH_Link
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATContentTypes.content.event import ATEvent

#zope.interface.classImplements(ATNewsItem, IOSHContent)
#zope.interface.classImplements(ATEvent, IOSHContent)
zope.interface.classImplements(OSH_Link, IOSHContent)

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.VocabularyPickerWidget.VocabularyPickerWidget import VocabularyPickerWidget

from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName

# dummy
DUMMY = False
tags_default = ['A']
tags_vocab = ['A', 'B', 'C']
dummy_vocab = ['this', 'is', 'a', 'dummy', 'vocabulary']
dummy_string = "this is a dummy string"



class ExtensionFieldMixin:
    def _Vocabulary(self, content_instance, vocab_name):
        if DUMMY:
            return atapi.DisplayList([(x, x) for x in dummy_vocab])
        else:
            pv = getToolByName(content_instance, 'portal_vocabularies')
            VOCAB = getattr(pv, vocab_name, None)
            if VOCAB:
                return VOCAB.getDisplayList(VOCAB)
            else:
                return DisplayList()

    def translationMutator(self, instance):
        return self.getMutator(instance)


class NACEField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'NACE')


class SubcategoryField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):
    
    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Subcategory')


class CountryField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):
    
    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Country')


class MTSubjectField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):
    
    def Vocabulary(self, content_instance):
#        return atapi.DisplayList([(x, x) for x in dummy_vocab])
        return self._Vocabulary(content_instance, 'MultilingualThesaurus')


#class HTMLKeywordsField(ExtensionField, ExtensionFieldMixin, atapi.LinesField):
#    
#    def Vocabulary(self, content_instance):
#        return self._Vocabulary(content_instance, 'html_meta_keywords')


import zope.component
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender

class TaggingSchemaExtender(object):
    zope.interface.implements(IOrderableSchemaExtender)
    zope.component.adapts(IOSHContent)
    
    # currently (linguaPlone 2.2 unreleased) it is not possible to have langaugeIndependent fields
    # at least not within the schema extender
    # translating an object will lead to 
    #      Module Products.LinguaPlone.browser.translate, line 61, in __call__
    #      Module Products.LinguaPlone.I18NBaseObject, line 145, in addTranslation
    #      AttributeError: translation_mutator


    _fields = [
            NACEField('nace',
                schemata='categorization',
                languageIndependent=True,
                multiValued=True,
                widget=VocabularyPickerWidget(
                    label="NACE Code",
                    description="Set the Nace tag",
                    vocabulary="NACE",
                    label_msgid='label_nace',
                    description_msgid='help_nace',
                    i18n_domain='plone',
                ),
                translation_mutator="translationMutator",
            ),
            SubcategoryField('subcategory',
                schemata='categorization',
                enforceVocabulary=True,
                languageIndependent=True,
                multiValued=True,
                widget=VocabularyPickerWidget(
                    label="Subcategory (Site position)", 
                    description="Select a Subcategory where this item belongs to.",
                    vocabulary="Subcategory",
                    label_msgid='label_subcategory',
                    description_msgid='help_subcategory',
                    i18n_domain='plone',
                    ),
                translation_mutator="translationMutator",
            ),
            CountryField('country',
                schemata='categorization',
                enforceVocabulary=False,
                languageIndependent=True,
                multiValued=True,
                widget=MultiCountryWidget(
                    label="Countries",
                    description='Select one or more countries appropriate for this content',
                    description_msgid='help_country',
                    provideNullValue=1,
                    nullValueTitle="Select...",
                    label_msgid='label_country',
                    i18n_domain='osha',
                ),                
#                widget=VocabularyPickerWidget(
#                    label='Country',
#                    description='Select one or more countries appropriate for this content',
#                    vocabulary="Country",
#                    label_msgid='label_country',
#                    description_msgid='help_category',
#                    i18n_domain='plone',
#                ),
                translation_mutator="translationMutator",
            ),
#            HTMLKeywordsField('html_meta_keywords',
#                schemata='categorization',
#                enforceVocabulary=True,
#                languageIndependent=True,
#                widget=atapi.MultiSelectionWidget(
#                    label='HMTL meta keywords',
#                    description='Select one or more keywords. They will appear in the HTML header of this object'
#                ),
#                translation_mutator="translationMutator",
#            ),
            MTSubjectField('multilingual_thesaurus',
                schemata='categorization',
                enforceVocabulary=False,
                languageIndependent=True,
                multiValued=True,
                widget=VocabularyPickerWidget(
                    label='Multilingual Thesaurus Subject',
                    description='Select one or more entries',
                    vocabulary="MultilingualThesaurus",
                    label_msgid='label_category',
                    description_msgid='help_multilingual_thesaurus',
                    i18n_domain='plone',
                ),
                translation_mutator="translationMutator",
            ),
            
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields

    def getOrder(self, original):
        categorization = original['categorization']
        #idx = categorization.index('relatedItems')
        categorization.remove('nace')
        #categorization.remove('html_meta_keywords')
        categorization.remove('country')
        categorization.remove('multilingual_thesaurus')
        categorization.remove('subcategory')
        #categorization.insert(0, 'html_meta_keywords')
        categorization.insert(0, 'nace')
        categorization.insert(0, 'country')
        categorization.insert(0, 'multilingual_thesaurus')
        categorization.insert(0, 'subcategory')


        return original

#NOTE: These methods are called quite frequently, so it pays to optimise
#them.


zope.component.provideAdapter(TaggingSchemaExtender,
                              name=u"osha.metadata")

