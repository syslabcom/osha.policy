# Add additional fields to the standard content types
# For now I assume that nearly all fields only are relevant for OSHContent
# except:
#   - Keywords, which will be handled by the plone subject
#   - html_meta_keywords, which are used to optimize the SEO Keywords
#   -

import logging

import zope.interface

from plone.app.blob.content import ATBlob

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.link import ATLink
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.ATCountryWidget.Widget import MultiCountryWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.ATVocabularyManager.namedvocabulary import NamedVocabulary
from Products.Archetypes import atapi
from Products.Archetypes.Widget import KeywordWidget
from Products.Archetypes.utils import DisplayList
from Products.CMFCore.utils import getToolByName
from Products.CaseStudy.CaseStudy import CaseStudy
from Products.DataGridField import DataGridField, DataGridWidget
from Products.DataGridField.Column import Column
from Products.DataGridField.SelectColumn import SelectColumn
from Products.LinguaPlone.utils import generateMethods
from Products.OSHATranslations import OSHAMessageFactory as _
from Products.OSHContentLink.OSH_Link import OSH_Link
from Products.PloneHelpCenter.content.FAQ import HelpCenterFAQ
from Products.RALink.content.RALink import RALink
from Products.RichDocument.content.richdocument import RichDocument
from Products.VocabularyPickerWidget.VocabularyPickerWidget import VocabularyPickerWidget

try:
    from slc.treecategories.widgets.widgets import InlineTreeWidget
except ImportError:
    InlineTreeWidget = None

from osha.theme.vocabulary import AnnotatableLinkListVocabulary
from osha.whoswho.content.whoswho import whoswho

from osha.policy.adapter.subtyper import IAnnotatedLinkList
from osha.policy.interfaces import IOSHACommentsLayer

log = logging.getLogger('osha.policy/adapter/schemaextender.py')

LANGUAGE_INDEPENDENT_INITIALIZED = '_languageIndependent_initialized_oshapolicy'

class IOSHContent(zope.interface.Interface):
    """ OSHContent """

class IOSHContentCaseStudy(zope.interface.Interface):
    """ OSHContent for CaseStudy """

class IOSHFileContent(zope.interface.Interface):
    """ Interface for Files and Images """

class IOSHContentRALink(zope.interface.Interface):
    """ OSHContent for RALink"""

class IOSHContentEvent(zope.interface.Interface):
    """ OSHContent for Event """

class IOSHContentDocument(zope.interface.Interface):
    """ OSH Content for Document types """

class IOSHNewsItem(zope.interface.Interface):
    """ OSH Content for Document types """

zope.interface.classImplements(ATDocument, IOSHContentDocument)
zope.interface.classImplements(ATEvent, IOSHContentEvent)
zope.interface.classImplements(ATNewsItem, IOSHNewsItem)
zope.interface.classImplements(CaseStudy, IOSHContentCaseStudy)
zope.interface.classImplements(OSH_Link, IOSHContent)
zope.interface.classImplements(RALink, IOSHContentRALink)
zope.interface.classImplements(RichDocument, IOSHContentDocument)
zope.interface.classImplements(whoswho, IOSHContentDocument)

# The cool new widget is used for the following, enabling bulk-tagger support
# Publications / Files / Images / Regular Links
zope.interface.classImplements(ATFile, IOSHFileContent)
zope.interface.classImplements(ATBlob, IOSHFileContent)
zope.interface.classImplements(ATImage, IOSHFileContent)
zope.interface.classImplements(ATLink, IOSHFileContent)

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


class NACEField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'NACE')


class SubcategoryField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Subcategory')


class CountryField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'Country')


class MTSubjectField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'MultilingualThesaurus')

class OSHAMetadataField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):

    def Vocabulary(self, content_instance):
        return self._Vocabulary(content_instance, 'OSHAMetadata')

class AttachmentField(ExtensionField, atapi.FileField):
    """ additional file field for attachments """

class ReferencedContentField(ExtensionFieldMixin, ExtensionField, atapi.ReferenceField):
    """ Possibility to reference content objects, the text of which """
    """ can be used to display inside the current object. """

class NewsMarkerField(ExtensionFieldMixin, ExtensionField, atapi.BooleanField):
    """ marker field to have object appear in news portlet """

class SEDataGridField(ExtensionFieldMixin, ExtensionField, DataGridField):
    """ marker field to have object appear in news portlet """

class BaseLinesField(ExtensionFieldMixin, ExtensionField, atapi.LinesField):
    """ """

class ReindexTranslationsField(ExtensionField, atapi.BooleanField):
    """ indicate whether translations should be reindexd upon saving """

description_reindexTranslations = \
    u"Check this box to have all translated versions reindexed. This is " \
    u"useful when you change language-independent fields suchs as dates " \
    u"and want the changes to be effective in the catalog, too. WARNING: " \
    u"depending on the number of translations, this will lead to " \
    u"a delay in the time it takes to save."

tagging_fields_dict = {
    'country':
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
                description= \
                    u'Select one or more countries appropriate for this '
                    u'content',
                description_msgid='help_country',
                provideNullValue=1,
                nullValueTitle="Select...",
                label_msgid='label_country',
                i18n_domain='osha',
            ),
        ),
    'subcategory':
        SubcategoryField('subcategory',
            schemata='default',
            enforceVocabulary=True,
            languageIndependent=True,
            multiValued=True,
            mutator='setSubcategory',
            accessor='getSubcategory',
            widget=VocabularyPickerWidget(
                label="Subcategory (Site position)",
                description= \
                    u'Choose the most relevant subcategories. This will '
                    u'decide where the information is displayed',
                vocabulary="Subcategory",
                label_msgid='label_subcategory',
                description_msgid='help_subcategory',
                i18n_domain='osha',
                condition="python:len(object.getField('subcategory').Vocabulary(object))",
            ),
        ),
    'multilingual_thesaurus':
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
    'nace':
        NACEField('nace',
            schemata='default',
            languageIndependent=True,
            multiValued=True,
            mutator='setNace',
            accessor='getNace',
            widget=VocabularyPickerWidget(
                label="Sector (NACE Code)",
                description= \
                    u"Pick one or more values by clicking the Add button or "
                    "using the Quicksearch field below.",
                vocabulary="NACE",
                label_msgid='label_nace',
                description_msgid='help_nace',
                i18n_domain='osha',
                condition="python:len(object.getField('nace').Vocabulary(object))",
            ),
        ),
    'osha_metadata':
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
                condition="python:len(object.getField('osha_metadata').Vocabulary(object))",
                ),
            vocabulary="OSHAMetadata"
        ),
    'isNews':
        NewsMarkerField('isNews',
            schemata='default',
            read_permission="Review portal content",
            write_permission="Review portal content",
            languageIndependent=True,
            default=False,
            mutator='setIsNews',
            accessor='getIsNews',
            widget=atapi.BooleanWidget(
                label="Mark as News",
                description="Check to have this appear as News in the portlet.",
                label_msgid='label_isnews',
                description_msgid='help_isnews',
                i18n_domain='osha',
            ),
        ),
    'ReindexTranslations':
        ReindexTranslationsField('reindexTranslations',
            schemata='default',
            default=False,
            languageIndependent=False,
            widget=atapi.BooleanWidget(
                label=u"Reindex translations on saving.",
                description=description_reindexTranslations,
                visible={'edit': 'visible', 'view': 'invisible'},
                condition="python:object.isCanonical()",
            ),
        ),
    'annotatedlinklist':
        SEDataGridField('annotatedlinklist',
            schemata='default',
            enforceVocabulary=False,
            languageIndependent=False,
            required=False,
            multiValued=True,
            columns=("linktext", "title", "url", "section"),
            widget = DataGridWidget(
                label=u"List of Links",
                description= \
                    u"Add as many links as you wish by adding new rows on "
                    u"the right. Choose a section from the dropdown to order "
                    u"the links.",
                columns={
                    'linktext' : Column("Linktext"),
                    'title' : Column("Title"),
                    'url' : Column("URL"),
                    'section' : SelectColumn("Section", vocabulary=AnnotatableLinkListVocabulary()),
                    },
            ),
        ),
    }

class OSHASchemaExtender(object):
    """ This is the base class for all other schema extenders. It sets the 
        layer, the interfaces being implemented and provides a helper method 
        that generates accessors and mutators for language independent fields.
    """
    zope.interface.implements(
                        IOrderableSchemaExtender, 
                        IBrowserLayerAwareExtender
                        )
    layer = IOSHACommentsLayer

    def _generateMethodsForLanguageIndependentFields(self, fields):
        klass = self.context.__class__
        if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
            fields = [field for field in fields if field.languageIndependent]
            generateMethods(klass, fields)
            log.info("called generateMethods on %s (%s) " % (klass, self.__class__.__name__))
            setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)

    def getOrder(self, original):
        return original


class TaggingSchemaExtender(OSHASchemaExtender):
    zope.component.adapts(IOSHContent)

    _fields = tagging_fields_dict.values()

    def __init__(self, context):
        self.context = context
        _myfields= list()
        for f in self._fields:
            if f.getName() not in ['osha_metadata', 'annotatedlinklist']:
                new_f = f.copy()
                _myfields.append(new_f)
        self._myfields = _myfields
        self._generateMethodsForLanguageIndependentFields(self._myfields)

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


class TaggingSchemaExtenderCaseStudy(TaggingSchemaExtender):
    zope.component.adapts(IOSHContentCaseStudy)

    def __init__(self, context):
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

        self._generateMethodsForLanguageIndependentFields(fields)

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


class TaggingSchemaExtenderRALink(TaggingSchemaExtender):
    zope.component.adapts(IOSHContentRALink)

    def __init__(self, context):
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

        self._generateMethodsForLanguageIndependentFields(fields)

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


class TaggingSchemaExtenderEvent(TaggingSchemaExtender):
    zope.component.adapts(IOSHContentEvent)
    _localFields = [
            AttachmentField('attachment',
                schemata='default',
                widget=atapi.FileWidget(
                    label= _(u'osha_event_attachment_label', default=u'Attachment'),
                    description= _(u'osha_event_attachment_label',
                        default= \
                            u"You can upload an optional attachment that will "
                            u"be displayed with the event."),
                ),
            ),
        ]

    def __init__(self, context):
        self.context = context
        _myfields= list()
        for f in self._fields:
            new_f = f.copy()
            if new_f.getName() in ('subcategory', 'multilingual_thesaurus'):
                new_f.required = False
            if new_f.getName() not in ('nace',):
                _myfields.append(new_f)
        self._myfields = _myfields + self._localFields
        self._generateMethodsForLanguageIndependentFields(self._myfields)

    def getFields(self):
        return self._myfields


class PressReleaseExtender(OSHASchemaExtender):
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
                    description=
                            _(u'OSHAMetadata_description', 
                            default="Choose relevant metadata"),
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
                    description=
                        u"Select one or more content items. Their body text "
                        u"will be displayed as part of the press release",
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
                widget=atapi.BooleanWidget(
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
                widget=atapi.BooleanWidget(
                    label=u"Reindex translations on saving.",
                    description=description_reindexTranslations,
                    visible={'edit': 'visible', 'view': 'invisible'},
                    condition="python:object.isCanonical()",
                ),
            ),
        ]

    def __init__(self, context):
        self.context = context
        self._generateMethodsForLanguageIndependentFields(self._fields)

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
# HelpCenterFAQ
#
# HelpCenterFAQ uses the AddRemoveWidget 'subject' widget instead of
# the standard one. Since we have override the standard keyword.pt
# template in
# osha/theme/skins/osha_theme_custom_templates/widgets/keyword.pt to
# provide translations for the keywords, here we subtype HelpCenterFAQ
# so that it also uses the standard 'subject' widget.
###############################################################################

class IFAQExtender(zope.interface.Interface):
    """ Marker for FAQ extender """

zope.interface.classImplements(HelpCenterFAQ, IFAQExtender)

class FAQExtender(OSHASchemaExtender):
    zope.component.adapts(IFAQExtender)

    _fields = [
        tagging_fields_dict.get('multilingual_thesaurus'),
        tagging_fields_dict.get('nace'),
        tagging_fields_dict.get('subcategory'),

        BaseLinesField(
            name='subject',
            multiValued=1,
            accessor="Subject",
            searchable=True,
            widget=KeywordWidget(
                label=_(u'label_categories', default=u'Categories'),
                description=_(u'help_categories',
                                default=u'Also known as keywords, tags or labels, '
                                        'these help you categorize your content.'),
                ),
            ),
    ]

    def __init__(self, context):
        self.context = context
        self._generateMethodsForLanguageIndependentFields(self._fields)

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

## ERO schema extension is no longer set globally.
## We only want it on the ERO subsite. This is done via a locally registered adapter.
## For the mechanism, see five.localsitemanager.localsitemaqnager.txt
##zope.component.provideAdapter(TaggingSchemaExtenderERO,
##                              name=u"osha.metadata.ero")

class TaggingSchemaExtenderDocument(TaggingSchemaExtender):
    zope.component.adapts(IOSHContentDocument)

    def __init__(self, context):
        self.context = context
        _myfields= list()
        for f in self._fields:
            if f.getName() not in ('subcategory', 'isNews', 'annotatedlinklist') or \
                (f.getName()=='annotatedlinklist' and IAnnotatedLinkList.providedBy(context)):
                new_f = f.copy()
                _myfields.append(new_f)
        self._myfields = _myfields
        self._generateMethodsForLanguageIndependentFields(self._myfields)

    def getFields(self):
        return self._myfields


class TaggingSchemaExtenderDocument(TaggingSchemaExtender):
    zope.component.adapts(IOSHNewsItem)

    def __init__(self, context):
        self.context = context
        _myfields= list()
        for f in self._fields:
            if f.getName() not in ('subcategory', 'isNews', 'annotatedlinklist') or \
                (f.getName()=='annotatedlinklist' and IAnnotatedLinkList.providedBy(context)):
                new_f = f.copy()
                _myfields.append(new_f)
        self._myfields = _myfields
        self._generateMethodsForLanguageIndependentFields(self._myfields)

    def getFields(self):
        return self._myfields


class TaggingSchemaExtenderFileContent(OSHASchemaExtender):
    zope.component.adapts(IOSHFileContent)

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
            ReindexTranslationsField('reindexTranslations',
                schemata='default',
                default=False,
                languageIndependent=False,
                widget=atapi.BooleanWidget(
                    label=u"Reindex translations on saving.",
                    description=description_reindexTranslations,
                    visible={'edit': 'visible', 'view': 'invisible'},
                    condition="python:object.isCanonical()",
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
                if InlineTreeWidget:
                    new_f.widget = InlineTreeWidget(**widget_args)

            _myfields.append(new_f)
        self._myfields = _myfields
        self._generateMethodsForLanguageIndependentFields(self._myfields)

    def getFields(self):
        return self._myfields
        
