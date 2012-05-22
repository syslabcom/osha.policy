from Products.CMFCore.utils import getToolByName
from logging import getLogger
from Products.ZCatalog.ProgressHandler import ZLogHandler
import transaction

log = getLogger('osha.policy cleanup catalog')


def cleanup(self):
    cat = getToolByName(self, "portal_catalog")
    purl = getToolByName(self, "portal_url")
    portal = purl.getPortalObject()
    zcat = cat._catalog
    pghandler = ZLogHandler(1000)
    size = len(zcat.uids)
    pghandler.init('Remove stale items from catalog', size)
    for path in zcat.uids.keys():
        pghandler.report(cnt)
        try:
            obj = portal.restrictedTraverse(path)
        except:
            # XXX what to do?
            print "no object found for %s" % path
            continue
        if "/".join(obj.getPhysicalPath()) != path:
            # saved under an old path! kill it
            index = zcat.uids[path]
            del zcat.uids[path]
            del zcat.paths[index]
            zcat._length.change(-1)
            log.info('Kill old path: %s' % path)
    pghandler.finish()
    transaction.commit()
