import os
import unittest2 as unittest

from Globals import package_home
from osha.theme.config import product_globals
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import quickInstallProduct
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.testing import z2
from plone.testing.z2 import Browser
from StringIO import StringIO
from Testing import ZopeTestCase as ztc
from zope.configuration import xmlconfig


def startZServerSSH(local_port, user_at_hostname):
    """ startZServerSSH(9999, "star@eithniu")
    starts the ZServer and prints:
    ssh -L 9999:localhost:55017 star@eithniu
    (which you run from a terminal)
    """
    import transaction
    transaction.commit()
    host, port = ztc.utils.startZServer()
    print "\n\nssh -L %s:localhost:%s %s\n\n" % (
        local_port, port, user_at_hostname)
    import pdb; pdb.set_trace()


class OshaPolicy(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import osha.policy
        xmlconfig.file('configure.zcml', osha.policy,
            context=configurationContext)

        # required, otherwise we get Unauth
        z2.installProduct(app, 'Products.ATVocabularyManager')
        z2.installProduct(app, 'Products.PressRoom')
        z2.installProduct(app, 'Products.ATCountryWidget')
        z2.installProduct(app, 'Products.Collage')
        z2.installProduct(app, 'Products.PloneHelpCenter')
        z2.installProduct(app, 'Products.LinguaPlone')
        z2.installProduct(app, "Products.Relations")
        z2.installProduct(app, "osha.policy")

        # required for python scripts e.g. manage_add*
        z2.installProduct(app, 'Products.PythonScripts')

        # The zcml needs to be loaded for GS profiles which are
        # dependencies of osha.policy
        import Products.ATVocabularyManager
        self.loadZCML('configure.zcml', package=Products.ATVocabularyManager)
        import Products.CallForContractors
        self.loadZCML('configure.zcml', package=Products.CallForContractors)
        import Products.CaseStudy
        self.loadZCML('configure.zcml', package=Products.CaseStudy)
        import Products.Collage
        self.loadZCML('configure.zcml', package=Products.Collage)
        import Products.OSHContentLink
        self.loadZCML('configure.zcml', package=Products.OSHContentLink)
        import Products.LinguaPlone
        self.loadZCML('configure.zcml', package=Products.LinguaPlone)
        import Products.PloneHelpCenter
        self.loadZCML('configure.zcml', package=Products.PloneHelpCenter)
        import Products.PressRoom
        self.loadZCML('configure.zcml', package=Products.PressRoom)
        import Products.PublicJobVacancy
        self.loadZCML('configure.zcml', package=Products.PublicJobVacancy)
        import Products.Relations
        self.loadZCML('configure.zcml', package=Products.Relations)
        import Products.RichDocument
        self.loadZCML('configure.zcml', package=Products.RichDocument)
        import Products.Scrawl
        self.loadZCML('configure.zcml', package=Products.Scrawl)
        import osha.policy
        self.loadZCML('configure.zcml', package=osha.policy)
        import osha.theme
        self.loadZCML('configure.zcml', package=osha.theme)
        import slc.shoppinglist
        self.loadZCML('configure.zcml', package=slc.shoppinglist)
        import slc.xliff
        self.loadZCML('configure.zcml', package=slc.xliff)

        import slc.seminarportal
        self.loadZCML("configure.zcml", package=slc.seminarportal)

        # TODO: integrate these:
        # browserlayer.utils.register_layer(
        #     IOSHACommentsLayer, name='osha.policy')
        # component.provideAdapter(instanceSchemaFactory)

    def setUpPloneSite(self, portal):
        # Workaround for the importVocabularies setuphandler calls
        # createSimpleVocabs which throws:
        # KeyError: 'ACTUAL_URL'
        portal.REQUEST["ACTUAL_URL"] = portal.REQUEST["SERVER_URL"]

        # Install all the Plone stuff + content (including the
		# Members folder)
        applyProfile(portal, 'Products.CMFPlone:plone')
        applyProfile(portal, 'Products.CMFPlone:plone-content')

        # quick install ATVocabularyManager or else we don't have
        # portal.portal_vocabularies
        quickInstallProduct(portal, "Products.ATVocabularyManager")
        quickInstallProduct(portal, "Products.PloneHelpCenter")
        quickInstallProduct(portal, "Products.ATCountryWidget")
        quickInstallProduct(portal, "Products.Collage")
        quickInstallProduct(portal, "plonetheme.classic")
        quickInstallProduct(portal, "Products.LinguaPlone")

        applyProfile(portal, 'osha.policy:default')
        applyProfile(portal, 'osha.theme:default')

        # We need this imports here, otherwise we get an error
        from Products.CMFPlone.tests.utils import MockMailHost
        from Products.MailHost.interfaces import IMailHost

        # Mock MailHost
        mockmailhost = MockMailHost('MailHost')
        portal.MailHost = mockmailhost
        sm = portal.getSiteManager()
        sm.registerUtility(component=mockmailhost, provided=IMailHost)

        # Login as manager and create a test folder
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        portal.invokeFactory('Folder', 'folder')

        # Enable Members folder
        from plone.app.controlpanel.security import ISecuritySchema
        security_adapter = ISecuritySchema(portal)
        security_adapter.set_enable_user_folders(True)

        # Commit so that the test browser sees these objects
        portal.portal_catalog.clearFindAndRebuild()
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.ATVocabularyManager')
        z2.uninstallProduct(app, 'Products.PressRoom')
        z2.uninstallProduct(app, 'Products.ATCountryWidget')
        z2.uninstallProduct(app, 'Products.Collage')
        z2.uninstallProduct(app, 'Products.PloneHelpCenter')
        z2.uninstallProduct(app, 'Products.LinguaPlone')
        z2.uninstallProduct(app, 'Products.PythonScripts')
        z2.uninstallProduct(app, "Products.Relations")
        z2.uninstallProduct(app, "osha.policy")


OSHA_FIXTURE = OshaPolicy()
OSHA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OSHA_FIXTURE,), name="OshaPolicy:Integration")
OSHA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OSHA_FIXTURE,), name="OshaPolicy:Functional")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = OSHA_INTEGRATION_TESTING


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = OSHA_FUNCTIONAL_TESTING

    def getBrowser(self):
        """Create an instance of zope.testbrowser."""
        browser = Browser(self.layer['app'])
        browser.open(self.layer['portal'].absolute_url() + '/login_form')
        browser.getControl(name='__ac_name').value = TEST_USER_NAME
        browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
        browser.getControl(name='submit').click()
        self.assertIn('You are now logged in', browser.contents)
        return browser

    def loadfile(self, rel_filename):
        home = package_home(product_globals)
        filename = os.path.sep.join([home, rel_filename])
        data = StringIO(open(filename, 'r').read())
        data.filename = os.path.basename(rel_filename)
        return data
