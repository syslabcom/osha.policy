 # -*- coding: utf-8 -*-
"""Tests for the practical_solutions portlet."""

from osha.policy.tests.base import IntegrationTestCase
from osha.theme.portlets import practical_solutions
from p4a.subtyper.interfaces import ISubtyper
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from slc.publications.interfaces import IPublicationContainerEnhanced
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides

import unittest2 as unittest


class TestPortlet(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='osha.PracticalSolutions')
        self.assertEquals(portlet.addview,
            'osha.PracticalSolutions')

    def test_interfaces(self):
        portlet = practical_solutions.Assignment(["agriculture"])
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='osha.PracticalSolutions')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={"subject": ["agriculture"]})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   practical_solutions.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = practical_solutions.Assignment(["agriculture"])
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, practical_solutions.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)

        assignment = practical_solutions.Assignment(["agriculture"])

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, practical_solutions.Renderer))


class TestRenderer(IntegrationTestCase):

    def setUp(self):
        """Custom shared utility setup for tests."""

        # shortcuts
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.view = self.portal.restrictedTraverse('@@plone')
        self.mapping = self.portal.restrictedTraverse('++contextportlets++plone.rightcolumn')
        self.manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        # enable osha.theme theme layer
        from osha.theme.browser.interfaces import IOSHAThemeLayer
        alsoProvides(self.request, IOSHAThemeLayer)

        # Publications are expected to support workflows
        self.workflow.setChainForPortalTypes(['File'], 'plone_workflow')

        # create a folder that will hold publications and change it's subtype
        # to PublicationContainer
        self.portal.invokeFactory('Folder', 'pubs', title='Publications')
        self.pubs = self.portal.pubs
        alsoProvides(self.pubs, IPublicationContainerEnhanced)
        self.subtyper = getUtility(ISubtyper)
        self.subtyper.change_type(self.pubs, u'slc.publications.FolderPublicationContainer')

        # add some publications
        self.pubs.invokeFactory('File', 'pub1')
        self.pubs.invokeFactory('File', 'pub2')
        self.pubs.invokeFactory('File', 'pub3')

        # set Subjects
        self.pubs.pub1.setSubject(['foo', 'bar'])
        self.pubs.pub2.setSubject(['foo', ])
        self.pubs.pub3.setSubject(['bar', ])

        # publish publications
        self.workflow.doActionFor(self.portal.pubs['pub1'], 'publish')
        self.workflow.doActionFor(self.portal.pubs['pub2'], 'publish')
        self.workflow.doActionFor(self.portal.pubs['pub3'], 'publish')

        # reindex everything to update the catalog
        [pub.reindexObject() for pub in self.pubs.values()]

    def _make_renderer(self, portlet):
        """Create an instance of portlet Renderer."""
        return queryMultiAdapter(
            (self.portal, self.request, self.view, self.manager, portlet),
            IPortletRenderer
        )

    def test_getRecentPublications(self):
        """Test output of getRecentPublications()."""
        portlet = practical_solutions.Assignment(subject=('foo',))
        renderer = self._make_renderer(portlet)
        results = renderer.getRecentPublications()
        self.assertEquals(len(results), 2)
        self.assertEquals(results[0].id, 'pub1')
        self.assertEquals(results[1].id, 'pub2')

    def test_getRecentPracticalSolutions(self):
        """Test output of getRecentPracticalSolutions()."""
        portlet = practical_solutions.Assignment(subject=('foo',))
        renderer = self._make_renderer(portlet)
        results = renderer.getRecentPracticalSolutions()
        self.assertEquals(len(results.keys()), 6)
        self.assertEquals(len(results['publications']), 2)
        self.assertEquals(results['publications'][0].id, 'pub1')
        self.assertEquals(results['publications'][1].id, 'pub2')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
