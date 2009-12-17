# -*- coding: utf-8 -*-

__author__ = """Syslab.com <info@syslab.com>"""
__docformat__ = 'plaintext'

from Products.CMFCore.permissions import setDefaultRoles

product_globals = globals()

DEFAULT_RIGHTS = "European Agency for Safety and Health at Work"
AUTHOR = "European Agency for Safety and Health at Work" # Set your default author here

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
    'FCKeditor',
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
    'slc.clicksearch',
    'slc.seminarportal',
    'collective.portlet.feedmixer',
    'collective.portlet.tal',
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
    'plone.app.ldap',
    'plone.app.blob',
    'syslabcom.filter',
    'plone.app.imaging',
    'qPloneCaptchas',
    'Scrawl',
    'qPloneComments',
    'p4a.plonevideo',
    'p4a.plonevideoembed',
    'Products.PloneFlashUpload',
    'BlueLinguaLink',
    'Calendaring',
    'RedirectionTool',
    'osha.legislation',
    'osha.theme',
    ]

    # XXX: Remove slc.alertservice and osha.legislation.
    # slc.alertservice is not found
    # osha.legislation throws 'invalid permission' error when being installed.

    # It is IMPORTANT that the linkchecker is installed at the end
    # because it relies on beforehand registered retrievers
    #quickinst.installProduct('CMFLinkChecker')


DEFAULT_FIELDS = {
    'CaseStudy':[
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
        ],

    "Image" : [
        'id',
        'title',
        'description',
        'image',
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'presentation',
        'tableContents',
        'cleanWordPastedText',
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
        'presentation',
        'tableContents',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
        'autoTranslateUploadedFiles',
        'ignoreDuplicateUploadedFiles',
        'customTranslationMatchingMethod',
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        ],

    "NewsItem" : [
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
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
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'language',
        'creators',
        'contributors',
        'rights',
        'cleanWordPastedText',
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
        'subject',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'cleanWordPastedText',
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
        'contact_name',
        'address',
        'phone',
        'fax',
        'email',
        'contact_url',
        'creators',
        'contributors',
        'rights',
        'cleanWordPastedText',
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'cleanWordPastedText',
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
        'allowDiscussion',
        'autoTranslateUploadedFiles',
        'ignoreDuplicateUploadedFiles',
        'customTranslationMatchingMethod',
        'subject',
        'location',
        'language',
        'description',
        'contributors',
        'creators',
        'rights',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
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
        'subject',
        'relatedItems',
        'location',
        'language',
        'effectiveDate',
        'expirationDate',
        'creation_date',
        'modification_date',
        'creators',
        'contributors',
        'rights',
        'allowDiscussion',
        'excludeFromNav',
        'nextPreviousEnabled',
        'cleanWordPastedText',
        'autoTranslateUploadedFiles',
        'ignoreDuplicateUploadedFiles',
        'customTranslationMatchingMethod',
        ],
    }
