# -*- coding: utf-8 -*-

__author__ = """Syslab.com <info@syslab.com>"""
__docformat__ = 'plaintext'

from Products.CMFCore.permissions import setDefaultRoles

product_globals = globals()

DEFAULT_RIGHTS = "European Agency for Safety and Health at Work"
# Set your default author here
AUTHOR = "European Agency for Safety and Health at Work"

PROJECTNAME = "OSHA"

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

DIFF_SUPPORT = [('OSH_Link', 'getText', 'Lines Diff')]

TYPES_TO_VERSION = ['OSH_Link', 'RichDocument', 'Document']

DEPENDENCIES = [
    'CMFPlacefulWorkflow',
    'plone.browserlayer',
    'plone.app.iterate',
    'LinguaPlone',
    'RichDocument',
    'Clouseau',
    'ATVocabularyManager',
    'Products.CallForContractors',
    'Marshall',
    'Products.OSHContentLink',
    'PublicJobVacancy',
    'slc.publications',
    'slc.autotranslate',
    'slc.editonpro',
    'slc.shoppinglist',
    'slc.xliff',
    'slc.foldercontentsfilter',
    'slc.subsite',
    'slc.seminarportal',
    'collective.portlet.feedmixer',
    'collective.portlet.tal',
    'pas.plugins.ldap',
    'plone.portlet.collection',
    'plone.portlet.static',
    'Products.VocabularyPickerWidget',
    'PressRoom',
    'Products.RALink',
    'Products.RemoteProvider',
    'PloneFormGen',
    'ATCountryWidget',
    'CMFSin',
    'Products.CaseStudy',
    'DataGridField',
    'TextIndexNG3',
    'UserAndGroupSelectionWidget',
    'plone.app.blob',
    'syslabcom.filter',
    'plone.app.imaging',
    'qPloneCaptchas',
    'Scrawl',
    'qPloneComments',
    'p4a.plonevideo',
    'p4a.plonevideoembed',
    'BlueLinguaLink',
    'Calendaring',
    'RedirectionTool',
    'osha.legislation',
# TODO: 4419    'osha.theme',
    'slc.calendarfetcher',
    'Products.feedfeeder',
    'Solgema.fullcalendar',
    ]

    # XXX: Remove slc.alertservice
    # slc.alertservice is not found

    # It is IMPORTANT that the linkchecker is installed at the end
    # because it relies on beforehand registered retrievers
    #quickinst.installProduct('CMFLinkChecker')


DEFAULT_FIELDS = {
    'CaseStudy': [
        'id',
        'title',
        'description',
        'isNews',
        'text',
        'displayImages',
        'action',
        'results',
        'publication_year',
        'organisation',
        'remoteLanguage',
        'remoteUrl',
        'displayAttachments',
        'subject',
        'relatedItems',
        'location',
        'osha_metadata',
        'nace',
        'country',
        'multilingual_thesaurus',
        'reindexTranslations',
        ],

    'Event': [
        'id',
        'title',
        'description',
        'isNews',
        'startDate',
        'endDate',
        'text',
        'attendees',
        'eventType',
        'eventUrl',
        'contactName',
        'contactEmail',
        'contactPhone',
        'subcategory',
        'multilingual_thesaurus',
        'osha_metadata',
        'attachment',
        'reindexTranslations',
        ],

    'HelpCenterFAQ': [
        'id',
        'title',
        'allowDiscussion',
        'description',
        'location',
        'creators',
        'effectiveDate',
        'expirationDate',
        'language',
        'creation_date',
        'modification_date',
        'answer',
        'versions',
        'sections',
        'contributors',
        'startHere',
        'subject',
        'relatedItems',
        'subcategory',
        'nace',
        'multilingual_thesaurus',
        ],

    "Link" : [
        'id',
        'title',
        'description',
        'isNews',
        'remoteUrl',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'reindexTranslations',
        ],

    "Image" : [
        'id',
        'title',
        'description',
        'isNews',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'reindexTranslations',
        'image',
        ],

    "File" : [
        'id',
        'title',
        'description',
        'isNews',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'reindexTranslations',
        'file',
        ],

    "Blob" : [
        'id',
        'title',
        'description',
        'isNews',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'reindexTranslations',
        'file',
        ],

    "Document" : [
        'id',
        'title',
        'description',
        'text',
        'country',
        'multilingual_thesaurus',
        'nace',
        'osha_metadata',
        'reindexTranslations',
        ],

    "RichDocument" : [
        'id',
        'title',
        'description',
        'text',
        'displayImages',
        'displayAttachments',
        'country',
        'multilingual_thesaurus',
        'nace',
        'osha_metadata',
        'reindexTranslations',
        ],

    "News Item" : [
        'id',
        'title',
        'description',
        'text',
        'image',
        'imageCaption',
        'country',
        'multilingual_thesaurus',
        'nace',
        'osha_metadata',
        'reindexTranslations',
        ],

    "RALink" : [
        'id',
        'title',
        'description',
        'isNews',
        'text',
        'remoteUrl',
        'remoteLanguage',
        'country',
        'remoteProvider',
        'multilingual_thesaurus',
        'nace',
        'dateOfEditing',
        'occupation',
        'ra_contents',
        'type_methodology',
        'subject',
        'allowDiscussion',
        'excludeFromNav',
        'tableContents',
        'presentation',
        'relatedItems',
        'location',
        'osha_metadata',
        'annotatedlinklist',
        'reindexTranslations',
        ],

    "OSH_Link" : [
        'id',
        'title',
        'description',
        'isNews',
        'text',
        'remoteUrl',
        'provider',
        'remoteProvider',
        'remoteLanguage',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'cas',
        'einecs',
        'general_comments',
        'author',
        'printref',
        'organisation_name',
        'isbn_d',
        'publication_date',
        'relatedItems',
        'language',
        'location',
        'excludeFromNav',
        'tableContents',
        'presentation',
        'allowDiscussion',
        'effectiveDate',
        'expirationDate',
        'reindexTranslations',
        ],

    "Provider" : [
        'id',
        'title',
        'description',
        'remoteUrl',
        'providerCategory',
        'subject',
        'allowDiscussion',
        'creation_date',
        'modification_date',
        'language',
        'remoteLanguage',
        'location',
        'effectiveDate',
        'expirationDate',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'isNews',
        'reindexTranslations',
    ],

    "PressRelease" : [
        'id',
        'releaseTiming',
        'title',
        'subhead',
        'releaseDate',
        'description',
        'text',
        'image',
        'imageCaption',
        'releaseContacts',
        'osha_metadata',
        'referenced_content',
        'isNews',
        'country',
        'reindexTranslations',
        ],

    "SPSpeaker" : [
        'id',
        'title',
        'firstName',
        'middleName',
        'lastName',
        'suffix',
        'email',
        'jobTitles',
        'officeAddress',
        'officeCity',
        'officeState',
        'officePostalCode',
        'officePhone',
        'image',
        'biography',
        'education',
        'website',
        'speeches',
        'nationality',
        'employer',
        'socialPartnerGroup',
        'expertise',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'isNews',
        'reindexTranslations',
        ],

    "SPSpeechVenue" : [
        'id',
        'title',
        'description',
        'isNews',
        'constrainTypesMode',
        'locallyAllowedTypes',
        'immediatelyAddableTypes',
        'country',
        'subcategory',
        'multilingual_thesaurus',
        'nace',
        'reindexTranslations',
        ],
    }
