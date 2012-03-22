from zope import component

from Testing import ZopeTestCase as ztc

from Products.Archetypes.Schema.factory import instanceSchemaFactory
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase import layer

from plone import browserlayer

from osha.policy.interfaces import IOSHACommentsLayer

SiteLayer = layer.PloneSite


class OSHAPolicyLayer(SiteLayer):

    @classmethod
    def setUp(cls):
        ptc.setupPloneSite(products=('osha.policy',))

        ztc.installProduct('ATVocabularyManager')
        ztc.installProduct('LinguaPlone')
        ztc.installProduct('ATCountryWidget')
        ztc.installProduct('TextIndexNG3')
        ztc.installProduct('ProxyIndex')
        ztc.installProduct('PressRoom')
        ztc.installProduct('Relations')
        ztc.installProduct('RALink')
        ztc.installProduct('CaseStudy')

        import osha.theme
        zcml.load_config('configure.zcml', osha.theme)
        import osha.policy
        zcml.load_config('configure.zcml', osha.policy)
        import slc.xliff
        zcml.load_config('configure.zcml', slc.xliff)
        import slc.shoppinglist
        zcml.load_config('configure.zcml', slc.shoppinglist)

        browserlayer.utils.register_layer(
            IOSHACommentsLayer, name='osha.policy')

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
