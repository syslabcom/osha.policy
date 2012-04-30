import unittest2 as unittest

from Products.CMFPlone.utils import getToolByName
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING


class TestOshMailView(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subscribe_email_sent(self):
        """Test if the subscription email is sent."""
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        oshmail_view = self.portal.restrictedTraverse('oshmail-view')
        oshmail_view.subscribe('sender@foo.bar', name='John Doe')

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: listserv@listserv.osha.europa.eu' in msg)
        self.assertTrue('From: John Doe <sender@foo.bar>' in msg)
        self.assertTrue('Subject: [No Subject]' in msg)
        self.assertTrue('SUBSCRIBE OSHMAIL anonymous' in msg)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
