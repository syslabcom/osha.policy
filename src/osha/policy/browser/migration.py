import transaction
from zope.app.component.hooks import getSite
import logging
import traceback
import transaction
from cStringIO import StringIO

from types import *
from datetime import datetime

from Products.Five import BrowserView

from Acquisition import aq_inner, aq_parent, aq_base, aq_chain, aq_get
from Products.CMFCore.utils import getToolByName

from Products.contentmigration.basemigrator.walker import Walker
from plone.app.blob.migrations import ATImageToBlobImageMigrator


count = 0

class ZopeFindImageWalker(Walker):
    def __init__(
        self, portal, migrator, **kwargs):
        self.portal = portal
        self.migrator = migrator
        self.src_portal_type = 'Image'
        self.src_meta_type = 'ATImage'
        self.dst_portal_type = 'Image'
        self.dst_meta_type = 'ATBlob'

        self.transaction_size = int(kwargs.get('transaction_size', 20))
        self.full_transaction = kwargs.get('full_transaction', False)
        self.use_savepoint = kwargs.get('use_savepoint', False)

        if self.full_transaction and self.use_savepoint:
            raise ValueError

        self.out = StringIO()
        self.counter = 0
        self.errors = []


    def go(self, **kwargs):
        """runner

        Call it to start the migration
        """
        self.migrate(self.walk(), **kwargs)

    def walk(self):
        top_node = self.portal.unrestrictedTraverse(
            "/osha/portal")

        for item in self._walk(top_node):
            if item is not None:
                yield itemh

    def _walk(self, node):
        global count
        if node.meta_type in ["Script (Python)", "External Method"]:
            return None
        for id, ob in node.ZopeFind(node, search_sub=0):
            if ob.meta_type == "ATImage":
                count += 1
                if count % 100 == 0:
                    print "Committing %s" %count
                    transaction.commit()
                print "%s %s" %(count, ob.absolute_url(1))
                if ob.getImage() is "":
                    print "Deleting %s" %ob.absolute_url(1)
                    parent = ob.aq_explicit.aq_parent
                    parent.manage_delObjects(ob.getId())
                else:
                    return ob
            else:
                # print "%s" %ob.absolute_url(1)
                self._walk(ob)
        return []


class MigrateImagesView(BrowserView):

    def __call__(self):
        portal = getSite()
        import pdb; pdb.set_trace()

        start_time = datetime.now()

        walker = ZopeFindImageWalker(
            portal, migrator=ATImageToBlobImageMigrator)
        walker.go()
        transaction.commit()

        print "Finished after %s seconds" %(datetime.now() - start_time)

