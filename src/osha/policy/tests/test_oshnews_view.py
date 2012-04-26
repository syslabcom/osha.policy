# -*- coding: utf-8 -*-
"""Tests for OSHA News Items views."""

import unittest2 as unittest

from osha.policy.tests.base import IntegrationTestCase


class TestOSHNewsLocalView(IntegrationTestCase):
    """Test for the @@oshanews-local-view."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        # create some dummy content
        # keep in mind that self.portal.news folder already exists
        self.portal.invokeFactory('Folder', 'othernews', title='Other News')

        self.portal.news.invokeFactory('News Item', 'newsitem1', title='A News Item')
        self.portal.news.invokeFactory('News Item', 'newsitem2', title='A Second News Item')
        self.portal.news.invokeFactory('News Item', 'newsitem3', title='A Draft News Item')
        self.portal.othernews.invokeFactory('News Item', 'newsitem4', title='A News Item in other folder')

        # publish news items, leave draft news item unpublished
        self.workflow.doActionFor(self.portal.news['newsitem1'], 'publish')
        self.workflow.doActionFor(self.portal.news['newsitem2'], 'publish')
        self.workflow.doActionFor(self.portal.othernews['newsitem4'], 'publish')

    def test_title(self):
        """The @@oshnews-local-view gets the title directly from context."""
        view = self.portal.news.unrestrictedTraverse('@@oshnews-local-view')
        self.assertEquals(view.Title(), 'News')

        view = self.portal.othernews.unrestrictedTraverse('@@oshnews-local-view')
        self.assertEquals(view.Title(), 'Other News')

    def test_get_results(self):
        """Test fetching news items for @@oshnews-local-view."""
        view = self.portal.news.unrestrictedTraverse('@@oshnews-local-view')
        results = view.getResults()

        # resulting news items must only be those that are contained in the
        # 'news' folder and are published
        self.assertEquals(len(results), 2)
        self.assertIn('newsitem1', [r.id for r in results])
        self.assertIn('newsitem2', [r.id for r in results])
        self.assertNotIn('newsitem3', [r.id for r in results])  # not published
        self.assertNotIn('newsitem4', [r.id for r in results])  # in another folder

    def test_getName(self):
        """Method getName() simply returns the name of the view."""
        view = self.portal.unrestrictedTraverse('@@oshnews-local-view')
        self.assertEquals(view.getName(), u'oshnews-local-view')


class TestOSHNewsView(IntegrationTestCase):
    """Test for the @@oshanews-view."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        # create some dummy content
        # keep in mind that self.portal.news folder already exists
        self.portal.invokeFactory('Folder', 'othernews', title='Other News')

        self.portal.news.invokeFactory('News Item', 'newsitem1', title='A News Item')
        self.portal.news.invokeFactory('News Item', 'newsitem2', title='A Second News Item')
        self.portal.news.invokeFactory('News Item', 'newsitem3', title='A Draft News Item')
        self.portal.othernews.invokeFactory('News Item', 'newsitem4', title='A News Item in other folder')

        # publish news items, leave draft news item unpublished
        self.workflow.doActionFor(self.portal.news['newsitem1'], 'publish')
        self.workflow.doActionFor(self.portal.news['newsitem2'], 'publish')
        self.workflow.doActionFor(self.portal.othernews['newsitem4'], 'publish')

    def test_title(self):
        """If called on an ATTopic, the @@oshnews-view gets the title from
        the ATTopic itself. Otherwise the title is a hardcoded translatable
        string.
        """
        # call on a ATTopic
        view = self.portal.news.aggregator.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.Title(), 'News')

        # call on something else
        view = self.portal.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.Title(), u'heading_newsboard_latest_news')

    def test_getName(self):
        """Method getName() simply returns the name of the view."""
        view = self.portal.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.getName(), u'oshnews-view')

    def test_showLinkToNewsItem(self):
        """If context has 'show_link_to_news_item' property set than its value
        gets returned, otherwise True.
        """
        # first test when property is not set
        view = self.portal.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.showLinkToNewsItem(), True)

        # now when property is set
        self.portal._setProperty('show_link_to_news_item', False)
        view = self.portal.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.showLinkToNewsItem(), False)

    def test_getBodyText(self):
        """Test that text of the context gets returned."""

        # test on a Folder, which does not have 'text' field
        view = self.portal.news.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.getBodyText(), '')

        # test on a News Item
        self.portal.news.newsitem1.setText('foo')
        view = self.portal.news.newsitem1.unrestrictedTraverse('@@oshnews-view')
        self.assertEquals(view.getBodyText(), 'foo')

    def test_getResults_on_ATTopic(self):
        """"Test results when @@oshnews-view is called on an ATTopic."""
        view = self.portal.news.aggregator.unrestrictedTraverse('@@oshnews-view')
        results = view.getResults()

        # results should be the same as the default Plone's 'News' ATTopic
        # displays -> all published News Items
        self.assertEquals(len(results), 3)
        self.assertEquals(results[0].id, 'newsitem1')
        self.assertEquals(results[1].id, 'newsitem2')
        self.assertEquals(results[2].id, 'newsitem4')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
