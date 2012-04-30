import unittest2 as unittest

from Products.CMFPlone.utils import getToolByName
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING


class TestEmailScripts(unittest.TestCase):
    """Test the skin scripts that send emails."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal.REQUEST["ACTUAL_URL"] = self.portal.REQUEST["SERVER_URL"]

    def _test_contact_us_method(self):
        """Basic test to see if the email is sent."""
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        self.portal.REQUEST['subject'] = 'Test email'
        self.portal.REQUEST['sender'] = 'Student'
        self.portal.REQUEST['email'] = 'sendto@foo.bar'
        self.portal.REQUEST['sender_from_address'] = 'sendfrom@foo.bar'
        self.portal.REQUEST['message'] = 'Message...'
        self.portal.REQUEST.form['form.button.Send'] = '1'

        self.portal.restrictedTraverse('contact_us_method')()

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: sendto@foo.bar' in msg)
        self.assertTrue('From: sendfrom@foo.bar' in msg)
        self.assertTrue('Subject: =?utf-8?q?Test_email' in msg)
        self.assertTrue('Message..' in msg)

    def test_oshmail_send(self):
        """Basic test to see if the email is sent."""
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        self.portal.invokeFactory('Collage', 'collage',
            title='Testing oshmail send', description='Testing...')
        self.portal['collage'].restrictedTraverse('oshmail_send')(
            'sendto@foo.bar')

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: sendto@foo.bar' in msg)
        self.assertTrue('From: news@osha.europa.eu' in msg)
        self.assertTrue('Subject: =?utf-8?q?Testing_oshmail_send' in msg)
        self.assertTrue('Testing...' in msg)

    def test_shortmessage_send(self):
        """Basic test to see if the email is sent."""
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        page_id = self.portal.folder.invokeFactory('Document', 'page',
            title='Test page')
        page = self.portal.folder[page_id]
        page.restrictedTraverse('shortmessage_send')('sendto@foo.bar')

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: sendto@foo.bar' in msg)
        self.assertTrue('From: news@osha.europa.eu' in msg)
        self.assertTrue('Subject: =?utf-8?q?Test_page' in msg)
        self.assertTrue('European Agency for Safety and Health at Work' in msg)

    def test_subscribeOSHMail(self):
        """Basic test to see if the email is sent."""
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        self.portal.REQUEST['emailaddress'] = 'sendfrom@foo.bar'
        self.portal.unrestrictedTraverse('subscribeOSHMail')()

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: listserv@listserv.osha.europa.eu' in msg)
        self.assertTrue('From: sendfrom@foo.bar' in msg)
        self.assertTrue('Subject: [No Subject]' in msg)
        self.assertTrue('SUBSCRIBE OSHMAIL anonymous' in msg)

    def test_send_feedback_site(self):
        """Basic test to see if the email is sent."""
        mailhost = getToolByName(self.portal, 'MailHost')
        mailhost.reset()

        self.portal.REQUEST['subject'] = 'Test email'
        self.portal.REQUEST['message'] = 'Message...'
        self.portal.REQUEST['sender_from_address'] = 'sendfrom@foo.bar'
        self.portal.restrictedTraverse('send_feedback_site')()

        # test email
        self.assertEqual(len(mailhost.messages), 1)
        msg = mailhost.messages[0]

        # test email headers and content
        self.assertTrue('To: comments@osha.europa.eu' in msg)
        self.assertTrue('From: comments@osha.europa.eu' in msg)
        self.assertTrue('Subject: =?utf-8?q?Test_email' in msg)
        self.assertTrue('Message..' in msg)

        # Now test if a custom email from address works
        mailhost.reset()
        self.portal.REQUEST['email_from_address'] = 'sendfrom@foo.bar'
        self.portal.restrictedTraverse('send_feedback_site')()
        msg = mailhost.messages[0]
        self.assertTrue('From: sendfrom@foo.bar' in msg)


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
