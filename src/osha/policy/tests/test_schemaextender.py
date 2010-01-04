import unittest
from Testing.ZopeTestCase import utils

from zope.component import adapter, getAdapters
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IExtensible

from archetypes.schemaextender import extender

from Products.PloneTestCase.setup import portal_owner, default_password

from osha.policy.config import product_globals
from osha.policy.config import DEFAULT_FIELDS

from base import OSHAPolicyTestCase

try:
    from plone.browserlayer.utils import registered_layers
    has_plone_browserlayer = True
except ImportError:
    # BBB, for naked plone 3.0, should be removed in future
    has_plone_browserlayer = False

# There are some problems creating these content types:
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

# These types are successfully extended
EXTENDED_TYPES = [
    'Link',
    'Image',
    'File',
    'Document',
    'CaseStudy',
    "PressRelease"
    ]


def startZServer(browser=None):
    host, port = utils.startZServer()
    print "http://%s:%s" %(host, port)
    print "%s:%s" %(portal_owner, default_password)


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

