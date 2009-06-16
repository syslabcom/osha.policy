from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import layer

SiteLayer = layer.PloneSite


class OSHAPolicyLayer(SiteLayer):

    @classmethod
    def setUp(cls):
        ptc.setupPloneSite(products=['osha.policy', 'CMFLinkChecker'])

        ztc.installProduct('ATVocabularyManager')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('ATCountryWidget')
        ztc.installProduct('TextIndexNG3')
        ztc.installProduct('ProxyIndex')
        ztc.installProduct('Relations')

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
