from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface, Attribute
from plone.portlets.interfaces import IPortletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """
    
class IDateTimeUtils(Interface):
    """Interface for DateTime formatting and conversion"""

    def toPortalTime(time=None, long_format=None):
        """given a time string, convert it into a DateTime and then format it appropariately"""

class INaceView(Interface):
    """Interface for displaying content by NACE code"""

    def resultsOverview(Categories=[],alphabetical=False):
        """Get a list of all NACE codes and number of objects found, optionally filtered by Categories"""

    def resultsByNACE(nace='', Categories=[]):
        """Get all objects with given NACE code, optionally filtered by Categories"""

class ITopicView(Interface):
    """Interface for displaying context by topic"""

    def resultsOverview(context, cat_uid=''):
        """Get a list of all sub-categories for the given category, and how many results
        are found for each"""

    def getResultsByCategory(Category='', byCountry=False):
        """Get results for the given category, optionally sorted by Country"""

class IVocabularyHelpers(Interface):
    """Interface that holds utility methods for working with AT Vocabularies"""

    def getUIDsByTerms(termList=[], vocabularyName=''):
        """A lookup is done for all term names in the list on the given Vocabulary.
        A list of the coresponding UIDs and the query string for the terms is returned"""

    def getHierarchyByName(vocabName):
        """Walk through the hierarchy of the Vocabulary denoted by vocabName and return the 
        hierarchy in form of a dict"""


class ISEPFolder(Interface):
    """ Marker Interface for Single Entry Point Folders """

class ISEPHelpers(Interface):
    """ Interface that holds utility methods for SEPs"""
    
    def getMySEP(context, REQUEST=None):
        """Gets the nearest folder of the context that is a SEPFolder"""

    def getCategories(context):
        """ Return the Categories set on context via Properties"""



class IVocabularyHelper(Interface):
    """Interface that holds verious methods for working with vocaularies"""

    def getDisplayListFor(vocabularyName=''):
        """ Return DisplayList for given vocabulary"""

    def getNaceList():
        """ Return DisplayList for Nace code """

    def getCountryList():
        """Return a display list of key-value pairs of the vocabulary 'Country',
        sorted in a fashion needed by OSHA"""

    def getSubjectList():
        """Return a display list of Subject entries"""


class IOSHAboveContent(IPortletManager):
    """we need our own portlet manager above the content area.
    """

class IOSHBelowContent(IPortletManager):
    """we need our own portlet manager below the content area.
    """

class ICaptchaHelper(Interface):
    """ This interface holds utility methods for using collective.captcha
    """

    def createCaptcha(context, request):
        """ Use context and request to create and return a Captcha object """

    def verifyCaptcha(context):
        """ Validate the user's input for a given captcha """


class IProviderHelper(Interface):
    """ This Interface holds methods for getting and displaying remote Providers 
    for a given object / Catalog brain
    """

    def getMyProviders(obj):
        """ Return all providers referenced by obj, which the current user has permission to view
        """