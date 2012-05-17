 # -*- coding: utf-8 -*-
"""Tests for the getPublicationsByKeyword python script."""

from zope.component import getUtility

import unittest2 as unittest

from osha.policy.tests.base import IntegrationTestCase


class TestGetPublicationsByKeywordScript(IntegrationTestCase):
    """Tests for the getPublicationsByKeyword python script."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = self.portal.folder
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.script = self.portal.get('getPublicationsByKeyword')

        # Change self.folder's subtype to PublicationFolder
        from p4a.subtyper.interfaces import ISubtyper
        self.subtyper = getUtility(ISubtyper)
        self.subtyper.change_type(self.folder, u'slc.publications.FolderPublicationContainer')
        self.assertEquals(
            self.subtyper.existing_type(self.folder).name,
            u'slc.publications.FolderPublicationContainer'
        )

        # Add a File to PublicationFolder -> it gets subtyped to a Publication
        # automatically because it's added to a PublicationFolder
        self.folder.invokeFactory('File', 'file')
        self.assertEquals(
            self.subtyper.existing_type(self.folder.file).name,
            u'slc.publications.Publication'
        )

        # publish test content
        self.workflow.doActionFor(self.folder, 'publish')
        self.workflow.doActionFor(self.folder.file, 'publish')

    def test_no_keywords(self):
        """TODO"""
        pass


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
