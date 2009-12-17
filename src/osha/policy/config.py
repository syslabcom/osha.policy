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
        ]
    }

