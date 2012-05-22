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
    cnt = removed = 0
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
            removed += 1
            log.info('Kill old path: %s' % path)
        cnt += 1
    pghandler.finish()
    import pdb; pdb.set_trace()
    log.info('Finished with the catalog, removed a total of %d items' % removed)
    log.info("Length: %d, len(uids): %d, len(paths): %d" % (zcat._length.value,
        len(zcat.uids), len(zcat.paths)))

    transaction.commit()
