import unittest2 as unittest

from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from zope.component import getUtility, getMultiAdapter

from osha.theme.portlets import practical_solutions
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING


class TestPortlet(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    # def populateSite(self):
    #     """ Populate the test site with some content. """
    #     setRoles(('Manager', ))
    #     portal_types = [ "OSH_Link", "RALink", "CaseStudy", "Provider"]
    #     self.portal.invokeFactory("Folder", "en")
    #     #import pdb; pdb.set_trace()
    #     for portal_type in portal_types:
    #         for i in range(5):
    #             id = "%s_%s" %(portal_type, i)
    #             # self.portal.en.invokeFactory(portal_type, id)
    #             _createObjectByType(portal_type, self, id)

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

    # def test_getBrainsBySection(self):
    #     """ Return a dict of section:[brains]
    #     """

    #     context = self.portal
    #     setRoles(('Manager', ))
    #     self.populateSite()
    #     pc = getToolByName(context, "portal_catalog")
    #     import pdb; pdb.set_trace()


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
