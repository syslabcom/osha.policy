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

import logging


LOG = logging.getLogger('P4 image2blob migration')

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

        self.transaction_size = int(kwargs.get('transaction_size', 50))
        self.full_transaction = kwargs.get('full_transaction', True)
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
        node = self.portal.unrestrictedTraverse(
            "/osha/portal")
        # while/blacklist for individual image ids
	id_whitelist = []
        id_blacklist = []
        # top-level images:
        for id, ob in node.ZopeFind(
            node, obj_metatypes=["ATImage",],search_sub=0):
            if len(id_whitelist) and id not in id_whitelist:
                continue
            if id in id_blacklist:
                continue
            if ob.getImage() == '':
                LOG.info('Image %s is empty, skipping' % ob.absolute_url(1))
                continue
            LOG.info("Migrating %s" %ob.absolute_url(1))
            yield ob
        folders = node.objectValues(['ATBTreeFolder', 'ATFolder'])
        # top-level folders
        # white/blacklist for folder ids
        whitelist = []
	blacklist = ['']
	for folder in folders:
            if len(whitelist) and folder.id not in whitelist:
                LOG.info("Whitelist. Skipping top-level folder %s" % folder.id)
                continue
            if len(blacklist) and folder.id in blacklist:
                LOG.info("Blacklist. Skipping top-level folder %s" % folder.id)
                continue
            for id, ob in folder.ZopeFind(
                folder, obj_metatypes=["ATImage",],search_sub=1):
		if len(id_whitelist) and id not in id_whitelist:
		    continue
                if id in id_blacklist:
                    continue
	        if ob.getImage() == '':
		    LOG.info('Image %s is empty, skipping' % ob.absolute_url(1))
                    continue
                LOG.info("Migrating %s" %ob.absolute_url(1))
                yield ob


class MigrateImagesView(BrowserView):
    """ NOTE: Apply "plone.app.blob: 'Image' replacement type" Types
    tool in portal_setup before runnig this.
    """

    def __call__(self):
        portal = getSite()

        # Getting a Doomed transaction for the first commit with the
        # sample database. Doing one transaction.commit() here is a
        # workaround
        # import pdb; pdb.set_trace()
        transaction.abort()

        start_time = datetime.now()

        walker = ZopeFindImageWalker(
            portal, migrator=ATImageToBlobImageMigrator)
        walker.go()
        transaction.commit()

        LOG.info("Finished after %s seconds" %(datetime.now() - start_time))

