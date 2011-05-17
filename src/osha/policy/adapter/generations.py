from zope.interface import implements
from zope.app.testing import ztapi
import transaction
from zope.app.generations.interfaces import IInstallableSchemaManager
from zope.app.generations.interfaces import ISchemaManager
from zope.app.generations.generations import SchemaManager
from zope.app.generations.generations import generations_key
from zope import component
from zope.app.testing import ztapi


class PortalUpdateManager(object):
    implements(IInstallableSchemaManager)

    # 0, 0 installs the update
    # if you add an evolve step, increase the min with 1 and the generation with 1 
    # a portal will only be upgraded to the min
    # the generation reflects the num of steps that you have vailable
    minimum_generation = 0
    generation = 0

    def get_portals(self, context):
        mountpoint = getattr(context, 'osha', None)
        if not mountpoint:
            return []
        return mountpoint.objectValues('Plone Site')

    def install(self, context):
        root = context.connection.root()
        app = root['Application']
        portals = self.get_portals(app)
                
        for portal in portals:
            portal.portal_javascripts.cache_duration = 14
            portal.portal_css.cache_duration = 14
            portal.portal_kss.cache_duration = 14

        transaction.commit()


    def evolve(self, context, generation):
        root = context.connection.root()
        app = root['Application']
        portals = self.get_portals(app)
                
        if generation == 1:
            for portal in portals:
                pass

        transaction.commit()

manager = PortalUpdateManager()
ztapi.provideUtility(ISchemaManager, manager, name='osha.policy')

