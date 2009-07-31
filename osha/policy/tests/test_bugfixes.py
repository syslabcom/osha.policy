from five.localsitemanager import make_objectmanager_site
from osha.policy.adapter.schemaextender import TaggingSchemaExtenderERO
import unittest
from zope.app.component.hooks import setSite as setActiveSite

from osha.policy.tests.base import OSHAPolicyFunctionalTestCase

class TestBugfixes(OSHAPolicyFunctionalTestCase):
    def test_3G_234(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('Folder', 'folder')
        folder = self.portal.folder
        make_objectmanager_site(folder)
        sitemanager = folder.getSiteManager()
    
        sitemanager.registerAdapter(factory=TaggingSchemaExtenderERO,
                                    name=u"osha.metadata.ero")
        setActiveSite(folder)

        folder.invokeFactory('RichDocument', 'maindoc')
        maindoc = folder.maindoc
        field = maindoc.Schema().getField('ero_target_group')
        self.assertTrue(field)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBugfixes))
    return suite
