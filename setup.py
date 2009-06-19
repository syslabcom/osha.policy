# -*- coding: utf-8 -*-
"""
This module contains the osha.policy package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.3'

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
    read('osha', 'policy', 'README.txt')
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
        ],
      keywords='osha portal policy egg',
      author='Syslab.com GmbH',
      author_email='info@syslab.com',
      url='https://svn.syslab.com/svn/OSHA/osha.policy',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'osha.theme',
          'collective.indexing',
          'collective.portlet.feedmixer',
          'collective.portlet.tal',
          'osha.legislation',
          'Products.ATVocabularyManager',
          'Products.CacheSetup',
          'Products.PloneFlashUpload',
          'Products.ProxyIndex',
    
          # -*- Extra requirements: -*-
      ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'osha.policy.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*- 
      """,
      paster_plugins = ["ZopeSkel"],
      )      
      
