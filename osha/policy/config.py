# -*- coding: utf-8 -*-
#
# File: config.py


__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'


from Products.CMFCore.permissions import setDefaultRoles

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
    'slc.editonpro',
    'slc.shoppinglist',
    'slc.xliff',
    'slc.foldercontentsfilter',
    'slc.alertservice',
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
    'simplon.plone.ldap',
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
    # It is IMPORTANT that the linkchecker is installed at the end
    # because it relies on beforehand registered retrievers
    #quickinst.installProduct('CMFLinkChecker')

product_globals = globals()

