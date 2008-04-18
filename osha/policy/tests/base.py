from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

# These are traditional products (in the Products namespace). They'd normally
# be loaded automatically, but in tests we have to load them explicitly. This
# should happen at module level to make sure they are available early enough.

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
ztc.installProduct('RiskAssessmentLink')
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


@onsetup
def setup_osha_policy():
    """Set up the additional products required for the OSHA site policy.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for the osha.policy package.
    # This includes the other products below as well.
    
    fiveconfigure.debug_mode = True
    import osha.policy
    zcml.load_config('configure.zcml', osha.policy)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
       
    ztc.installPackage('osha.theme')
    ztc.installPackage('osha.policy')
    
# The order here is important: We first call the (deferred) function which
# installs the products we need for the Optilux package. Then, we let 
# PloneTestCase set up this product on installation.

setup_osha_policy()
ptc.setupPloneSite(products=['osha.policy', 'CMFLinkChecker'])

class OSHAPolicyTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

class OSHAPolicyFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """