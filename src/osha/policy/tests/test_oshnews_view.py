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


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
