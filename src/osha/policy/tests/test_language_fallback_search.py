from Products.CMFPlone.utils import getToolByName
from collective.solr.interfaces import ISearch, ISolrConnectionConfig
from collective.solr.search import Search
from collective.solr.manager import SolrConnectionManager, SolrConnectionConfig
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.component import getMultiAdapter

import unittest2 as unittest
from mock import MagicMock


class TestLanguageFallbackSearch(unittest.TestCase):
    """OSHA requires that searches return translations in the
    preferred language where possible, and otherwise return
    English/Lanuage neutral items."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        
        en_id = self.portal.invokeFactory("Folder", id="en", title="English Folder")
        self.folder_en = self.portal[en_id]
        self.folder_en.setLanguage('en')
        
        # Make german top folder (will be called 'en-de', which is silly, but not a problem)
        self.folder_de = self.folder_en.addTranslation('de')
        
        self.folder_en.invokeFactory("Event", id="notrans-event", title="English Event with no translation")
        self.folder_en.invokeFactory("Event", id="en-event", title="English Event")
        de_event = self.folder_en['en-event'].addTranslation("de")
        request = self.portal.REQUEST
        request['set_language'] = 'de'
        self.portal.portal_languages.setLanguageBindings()

    def test_fallback_search(self):
        """Searching in the german folder should return also english untranslated events """
        lf_search_view = self.portal.restrictedTraverse("@@language-fallback-search")
        results = lf_search_view.search({"path": {"query":"/plone/en-de"}})
        self.assertEqual(set([x.getPath() for x in results]),
                         set(['/plone/en-de', '/plone/en-de/en-event', '/plone/en/notrans-event']))
        

    @unittest.skip("some problem with mock_search")
    def test_fallback_search_solr(self):
        """Basic test to test if the sendto method works (with basic
        template and no extra keyword arguments).  """
        mock_results = ['/plone/events', '/plone/events/aggregator', '/plone/events/en-event-de', '/plone/events/en-event']
        mock_search = Search()
        mock_search.getManager = lambda: SolrConnectionManager(active=True)
        mock_search.__call__ = MagicMock(return_value=mock_results)
        mock_search.search = mock_search.__call__
        sm = self.portal.getSiteManager()
        sm.registerUtility(component=SolrConnectionConfig(), provided=ISolrConnectionConfig)
        sm.registerUtility(component=mock_search, provided=ISearch)
        lf_search_view = self.portal.restrictedTraverse("@@language-fallback-search")
        results = lf_search_view.search_solr("path_parents:/plone/events")
        mock_search.assert_called_with("path_parents:/plone/events +Language:en OR all OR de")

def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
