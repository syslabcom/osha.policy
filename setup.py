# -*- coding: utf-8 -*-
"""
This module contains the osha.policy package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.3.45dev'

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
    
tests_require=['zope.testing']

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
        'collective.indexing',
        'collective.portlet.feedmixer',
        'collective.portlet.tal',
        'gocept.linkchecker',
        'osha.legislation',
        'osha.theme',
        'Products.ATCountryWidget',
        'Products.ATVocabularyManager',
        'Products.CacheSetup',
        'Products.LinguaPlone',
        'Products.PloneHelpCenter',
        'Products.PloneFlashUpload',
        'Products.ProxyIndex',
        'p4a.plonecalendar',
        'pypdf',
        'quintagroup.plonecaptchas',
        'quintagroup.plonecomments',
        'setuptools',
        'xlrd',
        'z3c.unconfigure',
        'zope.app.generations',
        'five.dbevent', 
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
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
      
