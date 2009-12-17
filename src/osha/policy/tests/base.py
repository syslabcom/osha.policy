from zope import interface
from zope import component

from Testing import ZopeTestCase as ztc

from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from plone.browserlayer import utils as browserlayerutils

from Products.Archetypes import atapi
from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer
from Products.PloneTestCase.layer import onsetup

from osha.policy.interfaces import IOSHACommentsLayer

SiteLayer = layer.PloneSite


class OSHAPolicyLayer(SiteLayer):

    @classmethod
    def setUp(cls):
        ptc.setupPloneSite(products=(
            'osha.policy',
            ))

        ztc.installProduct('ATVocabularyManager')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('ATCountryWidget')
        ztc.installProduct('TextIndexNG3')
        ztc.installProduct('ProxyIndex')
        ztc.installProduct('PressRoom')
        ztc.installProduct('RALink')
        ztc.installProduct('CaseStudy')


        import osha.theme
        zcml.load_config('configure.zcml', osha.theme)
        import osha.policy
        zcml.load_config('configure.zcml', osha.policy)
        import textindexng
        zcml.load_config('configure.zcml', textindexng)
        import slc.clicksearch
        zcml.load_config('configure.zcml', slc.clicksearch)
        import slc.xliff
        zcml.load_config('configure.zcml', slc.xliff)
        import slc.shoppinglist
        zcml.load_config('configure.zcml', slc.shoppinglist)

        component.provideAdapter(instanceSchemaFactory)
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
