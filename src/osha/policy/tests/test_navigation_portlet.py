from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from osha.theme.portlets import navigation
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.portlets.portlets import navigation as base_navigation
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from zope.component import getUtility, getMultiAdapter
from zope.interface import alsoProvides

import unittest2 as unittest


class TestPortlet(unittest.TestCase):
    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        from osha.theme.browser.interfaces import IThemeSpecific
        alsoProvides(self.layer['app'].REQUEST, IThemeSpecific)

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.leftcolumn',
                             context=self.portal)
        assignment = base_navigation.Assignment()

        renderer = getMultiAdapter((context, request, view, manager,
                                    assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, navigation.Renderer))


class TestRenderer(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        self._populate_site()
        from osha.theme.browser.interfaces import IThemeSpecific
        alsoProvides(self.layer['app'].REQUEST, IThemeSpecific)

    def renderer(self, context=None, request=None, view=None,
                 manager=None, assignment=None):
        context = context or self.portal
        request = request or self.layer['app'].REQUEST
        view = view or self.portal.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager,
            name='plone.leftcolumn', context=self.portal)
        assignment = assignment or base_navigation.Assignment(topLevel=0)

        return getMultiAdapter((context, request, view, manager,
                                assignment), IPortletRenderer)

    def _populate_site(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        if 'Members' in self.portal:
            self.portal._delObject('Members')
            self.folder = None
        if 'news' in self.portal:
            self.portal._delObject('news')
        if 'events' in self.portal:
            self.portal._delObject('events')
        if 'front-page' in self.portal:
            self.portal._delObject('front-page')
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory('Folder', 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.setRemoteUrl('http://plone.org')
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory('Folder', 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')

        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def test_create_navtree(self):
        view = self.renderer(self.portal)
        view.update()
        self.failUnless(view.tree)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the classes above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
