from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import layer

SiteLayer = layer.PloneSite


class OSHAPolicyLayer(SiteLayer):

    @classmethod
    def getPortal(cls):
        import pdb;pdb.set_trace()
        app = ZopeTestCase.app()
        portal = app._getOb(portal_name)
        _placefulSetUp(portal)
        return portal

    @classmethod
    def setUp(cls):
        ptc.setupPloneSite(products=['osha.policy', 'CMFLinkChecker'])

        ztc.installProduct('ATVocabularyManager')
        ztc.installProduct('CallForContractors')
        ztc.installProduct('CaseStudy')
        ztc.installProduct('CMFSin')
        ztc.installProduct('CMFLinkChecker')
        ztc.installProduct('Clouseau')
        ztc.installProduct('FCKeditor')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('OSHContentLink')
        ztc.installProduct('Publications')
        ztc.installProduct('PublicJobVacancy')
        ztc.installProduct('RALink')
        ztc.installProduct('SEPStructure')
        ztc.installProduct('VocabularyPickerWidget')
        ztc.installProduct('CMFPlacefulWorkflow')
        ztc.installProduct('plone.browserlayer')
        ztc.installProduct('plone.app.iterate')
        ztc.installProduct('RichDocument')
        ztc.installProduct('Marshall')
        ztc.installProduct('collective.portlet.feedmixer')
        ztc.installProduct('collective.portlet.tal')
        ztc.installProduct('plone.portlet.collection')
        ztc.installProduct('plone.portlet.static')
        #ztc.installProduct('PressRoom')
        ztc.installProduct('ATCountryWidget')
        ztc.installProduct('DataGridField')
        ztc.installProduct('TextIndexNG3')
        ztc.installProduct('UserAndGroupSelectionWidget')
        ztc.installProduct('simplon.plone.ldap')
        ztc.installProduct('ProxyIndex')
        ztc.installProduct('ZCatalog')
        ztc.installProduct('Relations')

        fiveconfigure.debug_mode = True
        import osha.policy
        import slc.seminarportal
        zcml.load_config('configure.zcml', osha.policy)
        zcml.load_config('configure.zcml', slc.seminarportal)
        fiveconfigure.debug_mode = False

        # We need to tell the testing framework that these products
        # should be available. This can't happen until after we have loaded
        # the ZCML.

        ztc.installPackage('osha.theme')
        ztc.installPackage('osha.policy')
        ztc.installPackage('slc.seminarportal')
        ztc.installPackage('osha.legislation')

        SiteLayer.setUp()



class OSHAPolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    layer = OSHAPolicyLayer

class OSHAPolicyFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """
    layer = OSHAPolicyLayer
