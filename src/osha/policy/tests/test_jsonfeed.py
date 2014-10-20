from DateTime import DateTime
from Testing.makerequest import makerequest
from mock import Mock
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.http import IHTTPRequest

from osha.policy.tests.base import IntegrationTestCase


class ISearchContext(Interface):
    """ """


mock_search = Mock()
mock_search.search = Mock(side_effect=lambda query: [])


class MockSearchFactory(object):
    implements(IBrowserView)

    def __new__(self, *objects):
        return mock_search


class TestJSONFeed(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        context_id = self.portal.invokeFactory(
            "Folder", id="search_context", title="Search Context")
        self.search_context = self.portal.get(context_id)
        alsoProvides(self.search_context, ISearchContext)

        gsm = getGlobalSiteManager()
        gsm.registerAdapter(
            MockSearchFactory, (ISearchContext, IHTTPRequest),
            name='language-fallback-search')
        requestobj = makerequest(self.portal.search_context)
        self.request = requestobj.REQUEST
        self.json_feed = getMultiAdapter(
            (self.portal.search_context, self.request), name='jsonfeed')

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            MockSearchFactory, (ISearchContext, IHTTPRequest),
            name='language-fallback-search')

    def test_start_end_date(self):
        """To include ongoing events, we must query for events that start at
        the requested end date or earlier and end at the requested start date
        or later. See also plone.app.event.base.get_events"""
        self.request.form = {
            'portal_type': 'mock',
            'Subject': 'mock',
            'path': '/mock',
            'Language': 'mock',
            'start': '2014-10-01T08:00:00+1',
            'end': '2014-10-31T08:00:00+1',
        }
        expected_query = {
            'sort_on': 'effective',
            'sort_order': 'descending',
            'portal_type': 'mock',
            'Subject': ['mock'],
            'path': '/plone/mock',
            'Language': 'mock',
            'start': {
                'query': DateTime('2014-10-31T08:00:00+1'),
                'range': 'max',
            },
            'end': {
                'query': DateTime('2014-10-01T08:00:00+1'),
                'range': 'min',
            },
            'object_provides': '',
        }
        self.json_feed.query()
        mock_search.search.assert_called_with(expected_query)
