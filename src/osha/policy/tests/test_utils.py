"""Test various osha utils."""

import unittest2 as unittest

from osha.policy.tests.base import OSHA_INTEGRATION_TESTING


class TestEnableJSView(unittest.TestCase):
    """Test @@osha-enable-js view from osha.theme"""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_call(self):
        """ """
        self.portal.invokeFactory('Document', 'page')
        page = self.portal['page']

        # for default view js should be enabled
        self.assertEqual(page.restrictedTraverse('@@osha-enable-js')(), True)

        # now set another view for the page, js should be disabled
        page.setLayout('oshnews-view')
        self.assertEqual(page.restrictedTraverse('@@osha-enable-js')(), False)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
