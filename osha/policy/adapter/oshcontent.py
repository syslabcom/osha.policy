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

class IOSHContentCaseStudy(zope.interface.Interface):
    """OSHContent for CaseStudy
    """

from Products.Archetypes.utils import DisplayList

from Products.ATCountryWidget.Widget import CountryWidget, MultiCountryWidget


# Provider
from Products.RemoteProvider.content.Provider import Provider
zope.interface.classImplements(Provider, IOSHContent)

#OSHLink
from Products.OSHContentLink.OSH_Link import OSH_Link
zope.interface.classImplements(OSH_Link, IOSHContent)

# RiskAssessmentLink
from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink
zope.interface.classImplements(RiskAssessmentLink, IOSHContent)

# Case Study
from Products.CaseStudy.CaseStudy import CaseStudy
zope.interface.classImplements(CaseStudy, IOSHContentCaseStudy)

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
        return self._Vocabulary(content_instance, 'MultilingualThesaurus')


class ReferencedContentField(ExtensionField, ExtensionFieldMixin, atapi.ReferenceField):
    """ Possibility to reference content objects, the text of which can be used to display inside the current object"""

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
            CountryField('country',
                schemata='default',
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
            ),
            SubcategoryField('subcategory',
                schemata='default',
                enforceVocabulary=True,
                languageIndependent=True,
                multiValued=True,
                widget=VocabularyPickerWidget(
                    label="Subcategory (Site position)", 
                    description="Select a Subcategory by clicking the Add button or by using the Quicksearch field below.",
                    vocabulary="Subcategory",
                    label_msgid='label_subcategory',
                    description_msgid='help_subcategory',
                    i18n_domain='plone',
                    ),
            ),
            MTSubjectField('multilingual_thesaurus',
                schemata='default',
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
            ),
            NACEField('nace',
                schemata='default',
                languageIndependent=True,
                multiValued=True,
                widget=VocabularyPickerWidget(
                    label="NACE Code",
                    description="Pick one or more values by clicking the Add button or using the Quicksearch field below.",
                    vocabulary="NACE",
                    label_msgid='label_nace',
                    description_msgid='help_nace',
                    i18n_domain='plone',
                ),
            ),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields

    def getOrder(self, original):
#        categorization = original.get('categorization', [])
#
#        if 'nace' in categorization:
#            categorization.remove('nace')
#        if 'country' in categorization:
#            categorization.remove('country')
#        if 'multilingual_thesaurus' in categorization:
#            categorization.remove('multilingual_thesaurus')
#        if 'subcategory' in categorization:
#            categorization.remove('subcategory')
#
#        categorization.insert(0, 'nace')
#        categorization.insert(0, 'country')
#        categorization.insert(0, 'multilingual_thesaurus')
#        categorization.insert(0, 'subcategory')
#        
#        original['categorization'] = categorization

        default = original.get('default', [])
        if 'remoteLanguage' in default:
            idx = default.index('remoteLanguage') + 1
            myfields = [x.getName() for x in self.getFields()]
            for myfield in myfields:
                if myfield in default:
                    default.remove(myfield)
            new_default = default[:idx] + myfields + default[idx:]
            original['default'] = new_default

        return original

#NOTE: These methods are called quite frequently, so it pays to optimise
#them.

zope.component.provideAdapter(TaggingSchemaExtender,
                              name=u"osha.metadata")


class TaggingSchemaExtenderCaseStudy(TaggingSchemaExtender):
    zope.interface.implements(IOrderableSchemaExtender)
    zope.component.adapts(IOSHContentCaseStudy)
    
    def __init__(self, context):
        super(TaggingSchemaExtender, self).__init__(self, context)
        for f in self._fields:
            if f.getName() in ('country', 'multilingual_thesaurus'):
                f.required = True
            elif f.getName() == 'subcategory':
                f.visible = dict(edit='invisible', view='invisible')

    def getOrder(self, original):
        default = original.get('default', [])
        
        if 'nace' in default:
            default.remove('nace')
        if 'country' in default:
            default.remove('country')
        if 'multilingual_thesaurus' in default:
            default.remove('multilingual_thesaurus')
        if 'subcategory' in default:
            default.remove('subcategory')
        
        default.append( 'nace')
        default.append( 'country')
        default.append( 'multilingual_thesaurus')
        default.append( 'subcategory')

        original['default'] = default

        return original

zope.component.provideAdapter(TaggingSchemaExtenderCaseStudy,
                              name=u"osha.metadata.casestudy")

###############################################################################
# Press Release
###############################################################################

class IPressReleaseExtender(zope.interface.Interface):
    """ Marker for PressRoom's PressRelease """

from Products.PressRoom.content.PressRelease import PressRelease
zope.interface.classImplements(PressRelease, IPressReleaseExtender)


class PressReleaseExtender(object):
    zope.interface.implements(IOrderableSchemaExtender)
    zope.component.adapts(IPressReleaseExtender)
    
    _fields = [
            ReferencedContentField('referenced_content',
                languageIndependent=True,
                multiValued=True,
                relationship='referenced_content',
                allowed_types=('Document', 'RichDocument'),
                widget=ReferenceBrowserWidget(
                    label=u"Referenced content",
                    description=u"Select one or more content items. Their body text will be displayed as part of the press release",
                    allow_search=True,
                    allow_browse=False,
                    base_query=dict(path=dict(query='textpieces', level=-1), Language=['en','']),
                    show_results_without_query=True,
                    ),
            ),
        ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields

    def getOrder(self, original):
        return original

zope.component.provideAdapter(PressReleaseExtender,
                              name=u"osha.metadata.pressrelease")


