# Add additional fields to the standard content types
# For now I assume that nearly all fields only are relevant for OSHContent
# except:
#   - Keywords, which will be handled by the plone subject
#   - html_meta_keywords, which are used to optimize the SEO Keywords
#   -

from Products.OSHATranslations import OSHAMessageFactory as _
from Products.LinguaPlone.utils import generateMethods
from zLOG import LOG, INFO
MODULE = 'osha.policy.schemaextender'
LANGUAGE_INDEPENDENT_INITIALIZED = '_languageIndependent_initialized_oshapolicy'
LANGUAGE_INDEPENDENT_INITIALIZED_ERO = '_languageIndependent_initialized_oshapolicy_ero'

import zope.interface
import zope.component
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender, IBrowserLayerAwareExtender
from osha.policy.interfaces import IOSHACommentsLayer

from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn

from slc.treecategories.widgets.widgets import InlineTreeWidget
from osha.policy.adapter.subtyper import IAnnotatedLinkList
from osha.theme.vocabulary import AnnotatableLinkListVocabulary



class IOSHContent(zope.interface.Interface):
    """OSHContent
    """

class IOSHContentCaseStudy(zope.interface.Interface):
    """OSHContent for CaseStudy
    """

class IOSHFileContent(zope.interface.Interface):
    """ Interface for Files and Images
    """

from Products.Archetypes.utils import DisplayList

from Products.ATCountryWidget.Widget import CountryWidget, MultiCountryWidget


# Provider
class IOSHContentProvider(zope.interface.Interface):
    """ OSHContent for Provider """

from Products.RemoteProvider.content.Provider import Provider
zope.interface.classImplements(Provider, IOSHContentProvider)

#OSHLink
from Products.OSHContentLink.OSH_Link import OSH_Link
zope.interface.classImplements(OSH_Link, IOSHContent)

#Regular Links
from Products.ATContentTypes.content.link import ATLink
zope.interface.classImplements(ATLink, IOSHContent)

# RALink
class IOSHContentRALink(zope.interface.Interface):
    """ OSHContent for RALink"""
from Products.RALink.content.RALink import RALink
zope.interface.classImplements(RALink, IOSHContentRALink)

# Case Study
from Products.CaseStudy.CaseStudy import CaseStudy
zope.interface.classImplements(CaseStudy, IOSHContentCaseStudy)

# Event
class IOSHContentEvent(zope.interface.Interface):
    """ OSHContent for Event """
from Products.ATContentTypes.content.event import ATEvent
zope.interface.classImplements(ATEvent, IOSHContentEvent)



# Document types
class IOSHContentDocument(zope.interface.Interface):
    """ OSH Content for Document types """
from Products.ATContentTypes.content.document import ATDocument
from Products.RichDocument.content.richdocument import RichDocument
from Products.ATContentTypes.content.newsitem import ATNewsItem
from osha.whoswho.content.whoswho import whoswho
zope.interface.classImplements(ATDocument, IOSHContentDocument)
zope.interface.classImplements(RichDocument, IOSHContentDocument)
zope.interface.classImplements(ATNewsItem, IOSHContentDocument)
zope.interface.classImplements(whoswho, IOSHContentDocument)

class IOSHNetworkDocument(zope.interface.Interface):
    """ OSHDocument for OSHNetwork """
#zope.interface.classImplements(ATDocument, IOSHNetworkDocument)


# Publications / Files / Images
from Products.ATContentTypes.content.file import ATFile
zope.interface.classImplements(ATFile, IOSHFileContent)
from plone.app.blob.content import ATBlob
zope.interface.classImplements(ATBlob, IOSHFileContent)
from Products.ATContentTypes.content.image import ATImage
zope.interface.classImplements(ATImage, IOSHFileContent)




from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.VocabularyPickerWidget.VocabularyPickerWidget import VocabularyPickerWidget

from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.Archetypes.Widget import BooleanWidget, KeywordWidget
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

    def getMutator(self, instance):
        def mutator(value, **kw):
            self.set(instance, value, **kw)
        methodName = getattr(self, 'mutator', None)
        if methodName is None:  # Use default setter
            return mutator
        
        method = getattr(instance, methodName, None)
        if method is None:   # Use default setter
            return mutator
        return method

#    def translationMutator(self, instance):
#        return self.getMutator(instance)


class NACEField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):
    pass

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'NACE')


class SubcategoryField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):
    pass

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Subcategory')


class CountryField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Country')


class MTSubjectField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):
    pass

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'MultilingualThesaurus')

class OSHAMetadataField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'OSHAMetadata')

class AttachmentField(ExtensionField, atapi.FileField):
    """ additional file field for attachments """

class ReferencedContentField(ExtensionFieldMixin, ExtensionField, atapi.ReferenceField):
    """ Possibility to reference content objects, the text of which can be used to display inside the current object"""

class NewsMarkerField(ExtensionFieldMixin, ExtensionField, atapi.BooleanField):
    """ marker field to have object appear in news portlet """

class SEDataGridField(ExtensionFieldMixin, ExtensionField, DataGridField):
    """ marker field to have object appear in news portlet """

class BaseLinesField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):
    pass

#class EroTargetGroupField(ExtensionField, atapi.LinesField):
#    """ target group for ERO """
#
#class EroTopicField(ExtensionField, atapi.LinesField):
#    """ topic for ERO """

class ReindexTranslationsField(ExtensionField, atapi.BooleanField):
    """ indicate whether translations should be reindexd upon saving """

description_reindexTranslations = u"Check this box to have all translated versions reindexed. This is useful when you " \
                            u"change language-independent fields suchs as dates and want the changes to be effective " \
                            u"in the catalog, too. WARNING: depending on the number of translations, this will lead to " \
                            u"a delay in the time it takes to save."




class TaggingSchemaExtender(object):
    zope.component.adapts(IOSHContent)
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    layer = IOSHACommentsLayer


    _fields = [
            CountryField('country',
                schemata='default',
                enforceVocabulary=False,
                languageIndependent=True,
                required=False,
                multiValued=True,
                mutator='setCountry',
                accessor='getCountry',
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
                mutator='setSubcategory',
                accessor='getSubcategory',
                widget=VocabularyPickerWidget(
                    label="Subcategory (Site position)",
                    description="Choose the most relevant subcategories. This will decide where the information is displayed",
                    vocabulary="Subcategory",
                    label_msgid='label_subcategory',
                    description_msgid='help_subcategory',
                    i18n_domain='osha',
                    condition="python:len(object.getField('subcategory').Vocabulary(object))",
                    ),
            ),
            MTSubjectField('multilingual_thesaurus',
                schemata='default',
                enforceVocabulary=False,
                languageIndependent=True,
                required=False,
                multiValued=True,
                mutator='setMultilingual_thesaurus',
                accessor='getMultilingual_thesaurus',
                widget=VocabularyPickerWidget(
                    label='Multilingual Thesaurus Subject',
                    description='Select one or more entries',
                    vocabulary="MultilingualThesaurus",
                    label_msgid='label_multilingual_thesaurus',
                    description_msgid='help_multilingual_thesaurus',
                    i18n_domain='osha',
                    condition="python:len(object.getField('multilingual_thesaurus').Vocabulary(object))",
                ),
            ),
            NACEField('nace',
                schemata='default',
                languageIndependent=True,
                multiValued=True,
                mutator='setNace',
                accessor='getNace',
                widget=VocabularyPickerWidget(
                    label="Sector (NACE Code)",
                    description="Pick one or more values by clicking the Add button or using the Quicksearch field below.",
                    vocabulary="NACE",
                    label_msgid='label_nace',
                    description_msgid='help_nace',
                    i18n_domain='osha',
                    condition="python:len(object.getField('nace').Vocabulary(object))",
                ),
            ),
            OSHAMetadataField('osha_metadata',
                schemata='default',
                enforceVocabulary=True,
                languageIndependent=True,
                multiValued=True,
                mutator='setOsha_metadata',
                accessor='getOsha_metadata',
                # translation_mutator='setTranslationOsha_metadata',
                widget=VocabularyPickerWidget(
                    label=_(u'OSHAMetadata_label', default=u"OSHA Metadata"),
                    description=_(u'OSHAMetadata_description', default="Choose relevant metadata"),
                    vocabulary="OSHAMetadata",
                    i18n_domain='osha',
                    condition="python:len(object.getField('osha_metadata').Vocabulary(object))",
                    ),
                vocabulary="OSHAMetadata"
            ),
            NewsMarkerField('isNews',
                schemata='default',
                read_permission="Review portal content",
                write_permission="Review portal content",
                languageIndependent=True,
                default=False,
                mutator='setIsNews',
                accessor='getIsNews',
                widget=BooleanWidget(
                    label="Mark as News",
                    description="Check to have this appear as News in the portlet.",
                    label_msgid='label_isnews',
                    description_msgid='help_isnews',
                    i18n_domain='osha',
                ),
            ),
            ReindexTranslationsField('reindexTranslations',
                schemata='default',
                default=False,
                languageIndependent=False,
                widget=BooleanWidget(
                    label=u"Reindex translations on saving.",
                    description=description_reindexTranslations,
                    visible={'edit': 'visible', 'view': 'invisible'},
                    condition="python:object.isCanonical()",
                ),
            ),
            SEDataGridField('annotatedlinklist',
                schemata='default',
                enforceVocabulary=False,
                languageIndependent=False,
                required=False,
                multiValued=True,
                columns=("linktext", "title", "url", "section"),
                widget = DataGridWidget(
                    label=u"List of Links",
                    description=u"Add as many links as you wish by adding new rows on the right. \
                                  Choose a section from the dropdown to order the links.",
                    columns={
                        'linktext' : Column("Linktext"),
                        'title' : Column("Title"),
                        'url' : Column("URL"),
                        'section' : SelectColumn("Section", vocabulary=AnnotatableLinkListVocabulary()),
                        },
                ),
            ),

        ]

    def __init__(self, context):
        self.context = context
        _myfields= list()
        for f in self._fields:
            if f.getName() not in ['osha_metadata', 'annotatedlinklist']:
                new_f = f.copy()
                _myfields.append(new_f)
        self._myfields = _myfields
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in _myfields if field.languageIndependent]
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

    def getFields(self):
        return self._myfields

    def getOrder(self, original):
        """ getting order """
        default = original.get('default', [])
        if 'remoteLanguage' in default:
            idx = default.index('remoteLanguage') + 1
            myfields = [x.getName() for x in self.getFields()]
            for myfield in myfields:
                if myfield in default:
                    default.remove(myfield)
            new_default = default[:idx] + myfields + default[idx:]
            original['default'] = new_default

        default = original.get('default', [])
        if 'isNews' in default and 'description' in default:
            default.remove('isNews')
            idx = default.index('description') + 1
            default.insert(idx, 'isNews')
        original['default'] = default

        default = original.get('default', [])
        if 'reindexTranslations' in default:
            default.remove('reindexTranslations')
            idx = len(default)
            default.insert(idx, 'reindexTranslations')
        original['default'] = default

        return original


# CaseStudy
class TaggingSchemaExtenderCaseStudy(TaggingSchemaExtender):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IOSHContentCaseStudy)
    layer = IOSHACommentsLayer

    def __init__(self, context):
        # (TaggingSchemaExtenderCaseStudy, self).__init__(context)
        self.context = context
        _myfields= list()
        for f in self._fields:
            new_f = f.copy()
            if new_f.getName() in ('country', 'multilingual_thesaurus'):
                new_f.required = True
            if new_f.getName() != 'subcategory':
                _myfields.append(new_f)
        self._myfields = _myfields
        # Case Study inherits from ATDocument. We might get a false positive, so check that the
        # accessors are really there
        initialized = True
        fields = [field for field in _myfields if field.languageIndependent]
        for field in fields:
            if not getattr(context, field.accessor, None):
                initialized = False
                break
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False) or not initialized:    
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

    def getFields(self):
        return self._myfields

    def getOrder(self, original):
        default = original.get('default', [])

        if 'nace' in default:
            default.remove('nace')
        if 'country' in default:
            default.remove('country')
        if 'multilingual_thesaurus' in default:
            default.remove('multilingual_thesaurus')

        default.append('nace')
        default.append('country')
        default.append('multilingual_thesaurus')

        original['default'] = default

        default = original.get('default', [])
        if 'isNews' in default:
            default.remove('isNews')
            idx = default.index('description') + 1
            default.insert(idx, 'isNews')
        original['default'] = default

        default = original.get('default', [])
        if 'reindexTranslations' in default:
            default.remove('reindexTranslations')
            idx = len(default)
            default.insert(idx, 'reindexTranslations')
        original['default'] = default

        return original


# RALink
class TaggingSchemaExtenderRALink(TaggingSchemaExtender):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IOSHContentRALink)
    layer = IOSHACommentsLayer

    def __init__(self, context):
        # super(TaggingSchemaExtenderRALink, self).__init__(context)
        self.context = context
        _myfields= list()
        for f in self._fields:
            new_f = f.copy()
            if new_f.getName() in ('country',): 
                new_f.required = True
            if new_f.getName() != 'subcategory':
                _myfields.append(new_f)
        self._myfields = _myfields
        # RA Link inherits from ATDocument. We might get a false positive, so check that the
        # accessors are really there
        initialized = True
        fields = [field for field in _myfields if field.languageIndependent]
        for field in fields:
            if not getattr(context, field.accessor, None):
                initialized = False
                break
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False) or not initialized:    
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

    def getFields(self):
        return self._myfields

    def getOrder(self, original):
        default = original.get('default', [])

        if 'remoteLanguage' in default:
            default.remove('nace')
            default.remove('country')
            default.remove('multilingual_thesaurus')
            idx = default.index('remoteLanguage') + 1
            new_default = default[:idx] + ['country'] \
                + [default[idx]] \
                + ['multilingual_thesaurus', 'nace'] \
                + default[idx+1:]
            original['default'] = new_default

        default = original.get('default', [])
        if 'isNews' in default:
            default.remove('isNews')
            idx = default.index('description') + 1
            default.insert(idx, 'isNews')
        original['default'] = default
 
        default = original.get('default', [])
        if 'reindexTranslations' in default:
            default.remove('reindexTranslations')
            idx = len(default)
            default.insert(idx, 'reindexTranslations')
        original['default'] = default

        return original



# Provider
class TaggingSchemaExtenderProvider(TaggingSchemaExtender):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IOSHContentProvider)
    layer = IOSHACommentsLayer

    def getOrder(self, original):
        return original

# Event
class TaggingSchemaExtenderEvent(TaggingSchemaExtender):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IOSHContentEvent)
    layer = IOSHACommentsLayer

    _localFields = [
            AttachmentField('attachment',
                schemata='default',
                widget=atapi.FileWidget(
                    label= _(u'osha_event_attachment_label', default=u'Attachment'),
                    description= _(u'osha_event_attachment_label',
                        default=u'You can upload an optional attachment that will be displayed with the event.'),
                ),
            ),
        ]

    def __init__(self, context):
        # super(TaggingSchemaExtenderEvent, self).__init__(context)
        self.context = context
        _myfields= list()
        for f in self._fields:
            new_f = f.copy()
            if new_f.getName() in ('subcategory', 'multilingual_thesaurus'):
                new_f.required = False
            if new_f.getName() not in ('country', 'nace'):
                _myfields.append(new_f)
        self._myfields = _myfields + self._localFields
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in _myfields if field.languageIndependent]
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)


    def getFields(self):
        return self._myfields


###############################################################################
# Press Release
###############################################################################

class IPressReleaseExtender(zope.interface.Interface):
    """ Marker for PressRoom's PressRelease """

from Products.PressRoom.content.PressRelease import PressRelease
zope.interface.classImplements(PressRelease, IPressReleaseExtender)


class PressReleaseExtender(object):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IPressReleaseExtender)
    layer = IOSHACommentsLayer

    _fields = [
            OSHAMetadataField('osha_metadata',
                schemata='default',
                enforceVocabulary=True,
                languageIndependent=True,
                multiValued=True,
                mutator='setOsha_metadata',
                accessor='getOsha_metadata',
                widget=VocabularyPickerWidget(
                    label=_(u'OSHAMetadata_label', default=u"OSHA Metadata"),
                    description=_(u'OSHAMetadata_description', default="Choose relevant metadata"),
                    vocabulary="OSHAMetadata",
                    i18n_domain='osha',
                    ),
                vocabulary="getOSHAMetadata"
            ),
            ReferencedContentField('referenced_content',
                languageIndependent=True,
                multiValued=True,
                relationship='referenced_content',
                allowed_types=('Document', 'RichDocument'),
                mutator='setReferenced_content',
                accessor='getReferenced_content',
                widget=ReferenceBrowserWidget(
                    label=u"Referenced content",
                    description=u"Select one or more content items. Their body text will be displayed as part of the press release",
                    allow_search=True,
                    allow_browse=False,
                    base_query=dict(path=dict(query='textpieces', level=-1), Language=['en','']),
                    show_results_without_query=True,
                    ),
            ),
            NewsMarkerField('isNews',
                schemata='default',
                read_permission="Review portal content",
                write_permission="Review portal content",
                languageIndependent=True,
                default=False,
                mutator='setIsNews',
                accessor='getIsNews',
                widget=BooleanWidget(
                    label="Mark as News",
                    description="Check to have this appear as News in the portlet.",
                    label_msgid='label_isnews',
                    description_msgid='help_isnews',
                    i18n_domain='osha',
                ),
            ),
            CountryField('country',
                schemata='default',
                enforceVocabulary=False,
                languageIndependent=True,
                required=False,
                multiValued=True,
                mutator='setCountry',
                accessor='getCountry',
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
            ReindexTranslationsField('reindexTranslations',
                schemata='default',
                default=False,
                languageIndependent=False,
                widget=BooleanWidget(
                    label=u"Reindex translations on saving.",
                    description=description_reindexTranslations,
                    visible={'edit': 'visible', 'view': 'invisible'},
                    condition="python:object.isCanonical()",
                ),
            ),
        ]

    def __init__(self, context):
        self.context = context
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in self._fields if field.languageIndependent]
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

    def getFields(self):
        return self._fields

    def getOrder(self, original):

        default = original.get('default', [])
        if 'reindexTranslations' in default:
            default.remove('reindexTranslations')
            idx = len(default)
            default.insert(idx, 'reindexTranslations')
        original['default'] = default

        return original



###############################################################################
# ERO
###############################################################################


#class IEROExtender(zope.interface.Interface):
#    """ Marker for ERO """
#
#
#zope.interface.classImplements(RichDocument, IEROExtender)
#
#
#class TaggingSchemaExtenderERO(object):
#    zope.interface.implements(IOrderableSchemaExtender)
#    zope.component.adapts(IEROExtender)
#
#
#    _fields = [
#           CountryField('country',
#               schemata='ERO',
#               mutator='setCountry',
#               accessor='getCountry',
#               enforceVocabulary=False,
#               languageIndependent=True,
#               required=False,
#               multiValued=True,
#               widget=MultiCountryWidget(
#                   label="Countries",
#                   description='Select one or more countries appropriate for this content',
#                   description_msgid='help_country',
#                   provideNullValue=1,
#                   nullValueTitle="Select...",
#                   label_msgid='label_country',
#                   i18n_domain='osha',
#               ),
#           ),
#           EroTargetGroupField('ero_target_group',
#               schemata='ERO',
#               mutator='setEro_target_group',
#               accessor='ero_target_group',
#               enforceVocabulary=False,
#               languageIndependent=True,
#               required=False,
#               multiValued=True,
#               widget=KeywordWidget(
#                   label=_(u'osha_ero_target_group_label', default=u'Target group'),
#                   description=_(u'osha_ero_target_group_description', default=u'Specifies the Target group for use in the Risk observatory'),
#               ),
#           ),
#           EroTopicField('ero_topic',
#               schemata='ERO',
#               mutator='setEro_topic',
#               accessor='ero_topic',
#               enforceVocabulary=False,
#               languageIndependent=True,
#               required=False,
#               multiValued=True,
#               widget=KeywordWidget(
#                   label=_(u'osha_ero_topic_label', default=u'Topic'),
#                   description=_(u'osha_ero_topic_description', default=u'Specifies the Topic for use in the Risk observatory'),
#               ),
#           ),
#       ]
#
#    def __init__(self, context):
#        self.context = context
#        klass = context.__class__
#        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED_ERO, False):
#            fields = [field for field in self._fields if field.languageIndependent]
#            generateMethods(klass, fields)
#            LOG(MODULE, INFO, "called generateMethods (ERO) on %s (%s) " % (klass, self.__class__.__name__))
#            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED_ERO, True)
#
#    def getFields(self):
#        return self._fields
#
#    def getOrder(self, original):
#        """ getting order """
#        return original
#
## ERO schema extension is no longer set globally.
## We only want it on the ERO subsite. This is done via a locally registered adapter.
## For the mechanism, see five.localsitemanager.localsitemaqnager.txt
##zope.component.provideAdapter(TaggingSchemaExtenderERO,
##                              name=u"osha.metadata.ero")



# Document
class TaggingSchemaExtenderDocument(TaggingSchemaExtender):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IOSHContentDocument)
    layer = IOSHACommentsLayer


    def __init__(self, context):
        # super(TaggingSchemaExtenderDocument, self).__init__(context)
        self.context = context
        _myfields= list()
        for f in self._fields:
            if f.getName() not in ('subcategory', 'isNews', 'annotatedlinklist') or \
                (f.getName()=='annotatedlinklist' and IAnnotatedLinkList.providedBy(context)):
                new_f = f.copy()
                _myfields.append(new_f)
        self._myfields = _myfields
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in _myfields if field.languageIndependent]
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)


    def getFields(self):
        return self._myfields




class TaggingSchemaExtenderFileContent(object):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(IOSHFileContent)
    layer = IOSHACommentsLayer



    _fields = [
            CountryField('country',
                schemata='default',
                enforceVocabulary=False,
                languageIndependent=True,
                required=False,
                multiValued=True,
                mutator='setCountry',
                accessor='getCountry',
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
            BaseLinesField('subcategory',
                schemata='default',
                enforceVocabulary=True,
                languageIndependent=True,
                multiValued=True,
                mutator='setSubcategory',
                accessor='getSubcategory',
                widget=VocabularyPickerWidget(
                    label="Subcategory (Site position)",
                    description="Choose the most relevant subcategories. This will decide where the information is displayed",
                    vocabulary="Subcategory",
                    label_msgid='label_subcategory',
                    description_msgid='help_subcategory',
                    i18n_domain='osha',
                    condition="python:len(object.getField('subcategory').Vocabulary(object))",
                    ),
            ),
            BaseLinesField('multilingual_thesaurus',
                schemata='default',
                enforceVocabulary=False,
                languageIndependent=True,
                required=False,
                multiValued=True,
                mutator='setMultilingual_thesaurus',
                accessor='getMultilingual_thesaurus',
                widget=VocabularyPickerWidget(
                    label='Multilingual Thesaurus Subject',
                    description='Select one or more entries',
                    vocabulary="MultilingualThesaurus",
                    label_msgid='label_multilingual_thesaurus',
                    description_msgid='help_multilingual_thesaurus',
                    i18n_domain='osha',
                    condition="python:len(object.getField('multilingual_thesaurus').Vocabulary(object))",
                ),
            ),
            BaseLinesField('nace',
                schemata='default',
                languageIndependent=True,
                multiValued=True,
                mutator='setNace',
                accessor='getNace',
                widget=VocabularyPickerWidget(
                    label="Sector (NACE Code)",
                    description="Pick one or more values by clicking the Add button or using the Quicksearch field below.",
                    vocabulary="NACE",
                    label_msgid='label_nace',
                    description_msgid='help_nace',
                    i18n_domain='osha',
                    condition="python:len(object.getField('nace').Vocabulary(object))",
                ),
            ),    
    
    ]
 
    def __init__(self, context):
        super(TaggingSchemaExtenderFileContent, self).__init__(context)
        _myfields = list()
        for field in self._fields:
            new_f = field.copy()
            if new_f.__name__ in ['subcategory','multilingual_thesaurus','nace']:
                vocabulary = NamedVocabulary(new_f.widget.vocabulary)
                widget_args = {}
                for arg in ('label', 'description', 'label_msgid', 
                            'description_msgid, i18n_domain'):
                    widget_args[arg] = getattr(new_f.widget, arg, '')
                widget_args['vocabulary'] = vocabulary
                new_f.vocabulary = vocabulary
                new_f.widget = InlineTreeWidget(**widget_args)
            _myfields.append(new_f)
        self._myfields = _myfields
        
        klass = context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in _myfields if field.languageIndependent]
            generateMethods(klass, fields)
            LOG(MODULE, INFO, "called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)



    def getFields(self):
        return self._myfields


    def getOrder(self, original):
        """ getting order """
        return original
        
        