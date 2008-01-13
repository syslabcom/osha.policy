from setuptools import setup, find_packages

version = '0.1'

setup(name='osha.policy',
      version=version,
      description="A policy to install an OSHA like portal",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='osha portal policy egg',
      author='syslabcom',
      author_email='info@syslab.com',
      url='https://svn.syslab.com/svn',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['osha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
