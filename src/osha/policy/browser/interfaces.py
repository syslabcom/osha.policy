from plone.portlets.interfaces import IPortletManager
from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 skin layer.
    """


class INaceView(Interface):
    """ Interface for displaying content by NACE code """

    def resultsOverview(Categories=[], alphabetical=False):
        """Get a list of all NACE codes and number of objects found,
        optionally filtered by Categories.
        """

    def resultsByNACE(nace='', Categories=[]):
        """Get all objects with given NACE code, optionally filtered by
        Categories.
        """


class ITopicView(Interface):
    """Interface for displaying context by topic"""

    def resultsOverview(context, cat_uid=''):
        """Get a list of all sub-categories for the given category, and how
        many results are found for each.
        """

    def getResultsByCategory(Category='', byCountry=False):
        """Get results for the given category, optionally sorted by Country"""


class IVocabularyHelpers(Interface):
    """Interface that holds utility methods for working with
    AT Vocabularies.
    """

    def getUIDsByTerms(termList=[], vocabularyName=''):
        """A lookup is done for all term names in the list on the given
        Vocabulary. A list of the coresponding UIDs and the query string
        for the terms is returned.
        """

    def getHierarchyByName(vocabName):
        """Walk through the hierarchy of the Vocabulary denoted by
        vocabName and return the hierarchy in form of a dict.
        """


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
        """Return a display list of key-value pairs of the vocabulary
        'Country', sorted in a fashion needed by OSHA.
        """

    def getSubjectList():
        """Return a display list of Subject entries"""


class IOSHAboveContent(IPortletManager):
    """We need our own portlet manager above the content area."""


class IOSHBelowContent(IPortletManager):
    """We need our own portlet manager below the content area."""


class ICaptchaHelper(Interface):
    """This interface holds utility methods for using collective.captcha."""

    def createCaptcha(context, request):
        """Use context and request to create and return a Captcha object."""

    def verifyCaptcha(context):
        """Validate the user's input for a given captcha."""


class IProviderHelper(Interface):
    """This Interface holds methods for getting and displaying remote
    Providers for a given object / Catalog brain.
    """

    def getMyProviders(obj):
        """Return all providers referenced by obj, which the current user
        has permission to view.
        """


class IPressroomHelper(Interface):
    """This Interface provides methods for the customized display of
    PressRoom objects.
    """

    def getTranslatedReferences(fieldname):
        """ Return a list of referenced items for the provided fieldname.
        The method is LinguaPlone aware.

        :param fieldname: [required] name of the field which contains
            referenced items
        """

    def getContacts(self):
        """Return contact info from the parent PressRoom object.
        The method is LinguaPlone aware.
        """


class ITranslationHelper(Interface):
    """Class with useful methods for working with translations."""

    def find_default(url, default='en'):
        """This method tries to find an object in the default language."""


class ILanguageFiles(Interface):
    """Class to set the language on all files inside the current folder
    according to their suffix.
    """


class ILCMaintenanceView(Interface):
    """Helper view that holds integration code for gocept.linkchecker."""

    def retrieve_and_notify():
        """Retrieve linkstates from zope to postgres and notify the lms on
        unregistered links this should be called by a cronjob nightly.
        """

    def notify_ws():
        """Notify the lms on unregistered links."""

    def update_pg(link_state='red', path_filter='',
                  multilingual_thesaurus=[], subcategory=[]):
        """Export the database to postgres."""

    def LinksInState(state, b_start=0, b_size=15, path_filter='',
                     multilingual_thesaurus=[], subcategory=[]):
        """Returns a list of links in the given state. It is possible to
        pass several filer parameters to narrow down the result."""


class IReportAbuse(Interface):
    """ """
