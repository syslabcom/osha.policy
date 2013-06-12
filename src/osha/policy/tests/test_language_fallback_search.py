from collective.solr.interfaces import ISearch, ISolrConnectionConfig
from collective.solr.parser import SolrResponse
from collective.solr.manager import SolrConnectionManager, SolrConnectionConfig
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

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

    @unittest.skip("using brains instead of flares fails with KeyError: 'htmltext_lexicon'")
    def test_fallback_search_solr(self):
        """Should work as test_fallback_search, but based on the native solr
           search utility """
        pc = api.portal.get_tool("portal_catalog")
        mock_results = SolrResponse()
        mock_results.response = pc({"path": {"query": "/plone/en-de"}})
        mock_search = MagicMock(return_value=mock_results)
        mock_search.getManager = lambda: SolrConnectionManager(active=True)
        from zope.interface import alsoProvides
        from plone.indexer.interfaces import IIndexableObject
        alsoProvides(mock_search, IIndexableObject)
        sm = self.portal.getSiteManager()
        sm.unregisterUtility(provided=ISearch)
        sm.unregisterUtility(provided=ISolrConnectionConfig)
        sm.registerUtility(component=SolrConnectionConfig(),
                           provided=ISolrConnectionConfig)
        sm.registerUtility(component=mock_search,
                           provided=ISearch)
        lf_search_view = self.portal.restrictedTraverse(
                "@@language-fallback-search")
        results = lf_search_view.search_solr("path_parents:/plone/events")
        self.assertEqual(set([x.getPath() for x in results]),
                         set(['/plone/en-de', '/plone/en-de/en-event', '/plone/en/notrans-event']))
        mock_search.search.assert_called_with(
                "path_parents:/plone/events +Language:en OR all OR de")


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
