# -*- coding: utf-8 -*-
"""
This module contains the osha.policy package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.3.39dev'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('src', 'osha', 'policy', 'README.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n'
    )

setup(name='osha.policy',
      version=version,
      description="A policy to install an OSHA like portal",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)",
        ],
      keywords='osha portal policy egg',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='https://svn.syslab.com/svn/OSHA/osha.policy',
      license='GPL + EUPL',
      packages=['osha', 'osha/policy'],
      package_dir = {'' : 'src'},
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Zope2',
        'StructuredText',
        'collective.portlet.feedmixer',
        'collective.portlet.tal',
        'osha.theme',
        'Products.ATVocabularyManager',
        'pypdf',
        'quintagroup.plonecaptchas',
        'setuptools',
        'z3c.unconfigure',
        'zope.app.generations',
        'zope.thread',
        'five.dbevent',
        'reportlab',
        'psycopg2',
        'python-ldap',
        'Pillow',
        'Plone',
        'Products.ATCountryWidget',
        'Products.AddRemoveWidget',
        'Products.ArchAddOn',
        'Products.CallForContractors',
        'Products.CaseStudy',
        'Products.DataGridField',
#        'Products.FCKeditor',
        'collective.ckeditor',
        'Products.LinguaPlone',
        'Products.MemcachedManager',
        'Products.OSHContentLink',
        'Products.PloneFormGen',
        'Products.PloneHelpCenter',
        'Products.PloneLDAP',
        'Products.PloneQueueCatalog',
        'Products.Ploneboard',
        'Products.Poi',
        'Products.PressRoom',
        'Products.PublicJobVacancy',
        'Products.QueueCatalog',
        'Products.RALink',
        'Products.RedirectionTool',
        'Products.Relations',
        'Products.RemoteProvider',
        'Products.RichDocument',
        'Products.Scrawl',
        'Products.TextIndexNG3',
        'SQLAlchemy',
        'archetypes.schemaextender',
        'archetypes.schematuning',
        'collective.captcha',
#        'collective.contentlicensing',
        'collective.contentrules.linguatarget',
        'collective.flowplayer',
        'collective.plonetruegallery',
        'collective.solr',
        'elementtree',
        'elementtreewriter',
        'gocept.linkchecker',
        'hachoir_core',
        'hachoir_metadata',
        'hachoir_parser=1.3.4',
        'osha.adaptation',
        'osha.aggregation',
        'osha.dynamicpressroom',
        'osha.eventrepository',
        'osha.fop',
        'osha.hw2010',
        'osha.searchurls',
        'osha.smartprintpublication',
        'osha.surveyanswers',
        'osha.whoswho',
        'p4a.common',
        'p4a.plonevideoembed',
        'p4a.subtyper',
        'plone.app.ldap',
        'plone.app.relations',
        'plone.app.z3cform',
        'plone.keyring',
        'plone.relations',
        'python-memcached',
        'quintagroup.ploneformgen.readonlystringfield',
        'skimpyGimpy',
        'slc.aggregation',
        'slc.alertservice',
        'slc.autotranslate [tests]',
        'slc.cleanwordpastedtext',
        'slc.dbtableedit',
        'slc.editonpro',
        'slc.foldercontentsfilter',
        'slc.googlesearch',
        'slc.linguatools',
        'slc.linkcollection',
        'slc.outdated',
        'slc.publications',
        'slc.quickchange',
        'slc.rdbploneformgenadapter',
        'slc.seminarportal',
        'slc.shoppinglist',
        'slc.subsite',
        'slc.synchronizer',
        'slc.xliff',
        'syslabcom.filter',
        'xlrd',
        'z3c.unconfigure',
        'zopyx.smartprintng.plone',
        'gocept.arecibologger',
        'Products.LongRequestLogger',
      ],
      extras_require={
        'test': ['zope.testing',],
        },
      test_suite = 'osha.policy.tests.test_docs.test_suite',
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      [console_scripts]
      converter = osha.policy.tools:converter
      vdexupdater = osha.policy.tools:vdexupdater
      xmltoxls = osha.policy.tools:xmltoxls
      ordervdex = osha.policy.tools:ordervdex
      find_missing_translations = osha.policy.tools:find_missing_translations
      insertTranslations = osha.policy.tools:insertTranslations
      """,
      )

