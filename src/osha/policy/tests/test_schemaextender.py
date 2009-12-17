import unittest

from base import OSHAPolicyTestCase

from osha.policy.config import product_globals
from osha.policy.config import DEFAULT_FIELDS

#    'Blob', no content type
#    'RichDocument', ua
#    'NewsItem', no content type

# (Pdb) self.portal.invokeFactory("SPSpeaker", "asdf")
# *** ValueError: No such content type: SPSpeaker
# (Pdb) self.portal.invokeFactory("SPSpeechVenue", "asdf")
# *** ValueError: No such content type: SPSpeechVenue
#slc.seminarportal
# (Pdb) self.portal.invokeFactory("HelpCenterFAQ", "asdf")
# *** ValueError: No such content type: HelpCenterFAQ
#PloneHelpCenter

EXTENDED_TYPES = [
    'Link',
    'Image',
    'File',
    'Document',
    'Event',
    'CaseStudy',
    'RALink',
    "PressRelease"
    ]

def startZServer(browser=None):
    host, port = utils.startZServer()
    if browser:
        print browser.url.replace('nohost', '%s:%s' % (host, port))


class TestSchemaExtender(OSHAPolicyTestCase):

    def afterSetUp(self):
        #self.setRoles(('Manager', ))
        self.loginAsPortalOwner()

    def populate_site(self):
        """
        Populate the test instance with content.
        """
        for type in EXTENDED_TYPES:
            # Create an object for each portal_type which is extended
            # The name is the same as the type
            self.portal.invokeFactory(type, type)

    def test_default_fields(self):
        """
        Test the extended schema of a document
        """
        self.populate_site()

        for type in EXTENDED_TYPES:
            obj = self.portal.get(type)

            default_schema = obj.Schema().getSchemataFields("default")
            fields = [i.__name__ for i in default_schema]
            self.assertEquals(
                DEFAULT_FIELDS[type],
                fields,
                "%s has the following Default fields: %s but should have %s"
                %(type, fields, DEFAULT_FIELDS[type]))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSchemaExtender))
    return suite

