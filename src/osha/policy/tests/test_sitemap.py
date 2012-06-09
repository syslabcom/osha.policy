 # -*- coding: utf-8 -*-
"""Tests for OSHA sitemap views."""

from osha.policy.tests.base import IntegrationTestCase
from zope.interface import alsoProvides

import unittest2 as unittest


class TestNewsMapView(IntegrationTestCase):
    """Test for the `newsmap.xml.gz` view that renders a Google newsmap."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        # enable osha.theme theme layer
        from osha.theme.browser.interfaces import IOSHAThemeLayer
        alsoProvides(self.request, IOSHAThemeLayer)

        # create some dummy content
        # sitemap expects a certain folder structure
        self.portal.invokeFactory('Folder', 'en')
        self.portal.en.invokeFactory('Folder', 'teaser')
        self.portal.en.invokeFactory('Folder', 'press')
        self.teaser = self.portal.en.teaser
        self.press = self.portal.en.press

        self.teaser.invokeFactory('News Item', 'newsitem1', title='A News Item')
        self.teaser.invokeFactory('News Item', 'newsitem2', title='An Outdated News Item')
        self.teaser.invokeFactory('News Item', 'newsitem3', title='A Draft News Item')
        self.press.invokeFactory('News Item', 'newsitem4', title='A News Item in other folder')

        # publish news items, leave draft news item unpublished
        self.workflow.doActionFor(self.teaser.newsitem1, 'publish')
        self.workflow.doActionFor(self.teaser.newsitem2, 'publish')
        self.workflow.doActionFor(self.press.newsitem4, 'publish')

        # mark newsitem2 as outdated
        self.teaser.newsitem2.unrestrictedTraverse("object_toggle_outdated").toggle()

    def test_objects(self):
        """Test data that is used to generate the Google newsmap."""
        view = self.portal.unrestrictedTraverse('@@newsmap.xml.gz')

        results = list(view.objects())
        self.assertEquals(len(results), 2)

        self.assertEquals(results[0]['loc'], 'http://nohost/plone/en/teaser/newsitem1')
        self.assertEquals(results[1]['loc'], 'http://nohost/plone/en/press/newsitem4')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
