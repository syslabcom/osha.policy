from zope import component
from zope.configuration import xmlconfig

from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase as ztc

from plone.app.testing import (
    FunctionalTesting, IntegrationTesting, PLONE_FIXTURE,
    PloneSandboxLayer, applyProfile, quickInstallProduct)
from plone.testing import z2

from osha.policy.interfaces import IOSHACommentsLayer


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

        # required for python scripts e.g. manage_add*
        z2.installProduct(app, 'Products.PythonScripts')
        # required, otherwise we get Unauth
        z2.installProduct(app, 'Products.ATVocabularyManager')

        z2.installProduct(app, 'Products.PressRoom')
        z2.installProduct(app, 'Products.ATCountryWidget')
        z2.installProduct(app, "Products.Relations")
        z2.installProduct(app, "osha.policy")

        # The zcml needs to be loaded for GS profiles which are
        # dependencies of osha.policy
        import Products.ATVocabularyManager
        self.loadZCML('configure.zcml', package=Products.ATVocabularyManager)
        import Products.Scrawl
        self.loadZCML('configure.zcml', package=Products.Scrawl)
        import osha.policy
        self.loadZCML('configure.zcml', package=osha.policy)
        import osha.theme
        self.loadZCML('configure.zcml', package=osha.theme)
        import slc.xliff
        self.loadZCML('configure.zcml', package=slc.xliff)
        import slc.shoppinglist
        self.loadZCML('configure.zcml', package=slc.shoppinglist)
        import Products.Relations
        self.loadZCML('configure.zcml', package=Products.Relations)
        import Products.PressRoom
        self.loadZCML('configure.zcml', package=Products.PressRoom)
        import Products.OSHContentLink
        self.loadZCML('configure.zcml', package=Products.OSHContentLink)

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

        # The default workflow needs to be set before adding plone-content
        wftool = getToolByName(portal, 'portal_workflow')
        wftool.setDefaultChain('plone_workflow')
        # Create the default plone portal content (do we need to?)
        applyProfile(portal, 'Products.CMFPlone:plone-content')

        # quick install ATVocabularyManager or else we don't have
        # portal.portal_vocabularies
        quickInstallProduct(portal, "Products.ATVocabularyManager")

        quickInstallProduct(portal, "Products.ATCountryWidget")

        applyProfile(portal, 'osha.policy:default')
        applyProfile(portal, 'osha.theme:default')


OSHA_FIXTURE = OshaPolicy()
OSHA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OSHA_FIXTURE,), name="OshaPolicy:Integration")
OSHA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OSHA_FIXTURE,), name="OshaPolicy:Functional")
