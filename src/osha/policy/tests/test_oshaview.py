import unittest2 as unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from Products.CMFPlone.utils import getToolByName
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING


class TestOshaView(unittest.TestCase):
    """Test the oshaview module."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_sendto_basic(self):
        """Basic test to test if the sendto method works (with basic template
        and no extra keyword arguments).
        """
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        oshaview = self.portal.restrictedTraverse('oshaview')
        oshaview.sendto(
            'sendto@foo.bar',
            'sentfrom@foo.bar',
            'Additional comment',
            subject='Test email'
        )

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: sendto@foo.bar' in msg)
        self.assertTrue('From: sentfrom@foo.bar' in msg)
        self.assertTrue('Subject: =?utf-8?q?Test_email' in msg)
        self.assertTrue('Additional comment' in msg)

    def _test_sendto_custom_template(self):
        """Test the custom sendto_template."""
        # TODO
        pass


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
