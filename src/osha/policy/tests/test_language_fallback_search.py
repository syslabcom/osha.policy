from Products.CMFPlone.utils import getToolByName
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from plone import api
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from zope.component import getMultiAdapter

import unittest2 as unittest


class TestLanguageFallbackSearch(unittest.TestCase):
    """OSHA requires that searches return translations in the
    preferred language where possible, and otherwise return
    English/Lanuage neutral items."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        events = self.portal.events
        events.invokeFactory("Event", id="en-event", title="English Event")
        de_event = events["en-event"].addTranslation("de")
        request = self.portal.REQUEST
        request['set_language'] = 'de'
        self.portal.portal_languages.setLanguageBindings()

    def test_fallback_search(self):
        """Basic test to test if the sendto method works (with basic
        template and no extra keyword arguments).  """
        lf_search_view = self.portal.restrictedTraverse("@@language-fallback-search")
        results = lf_search_view.search({"path": {"query":"/plone/events"}})
        self.assertEqual(set([x.getPath() for x in results]),
                         set(['/plone/events', '/plone/events/aggregator', '/plone/events/en-event-de']))


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
