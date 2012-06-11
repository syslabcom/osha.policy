from Products.CMFCore.utils import getToolByName
from logging import getLogger
from Products.ZCatalog.ProgressHandler import ZLogHandler
import transaction
from Acquisition import aq_parent

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
        cnt += 1
        try:
            obj = portal.restrictedTraverse(path)
        except:
            # XXX what to do?
            log.warning("no object found for %s" % path)
            cat.uncatalog_object(path)
            removed += 1
            log.info('Kill old path: %s' % path)
        else:
            if  "/".join(obj.getPhysicalPath()) != path:
                # saved under an old path! kill it
                cat.uncatalog_object(path)
                #index = zcat.uids[path]
                #del zcat.uids[path]
                #del zcat.paths[index]
                #zcat._length.change(-1)
                removed += 1
                log.info('Kill old path: %s' % path)
            else:
                parent = aq_parent(obj)
                ids = [x['id'] for x in parent._objects]
                if obj.getId() not in ids and obj.getId() not in parent.objectIds():
                    cat.uncatalog_object(path)
                    removed += 1
                    log.info('ID not found as a child of current parent, kill it: %s' % path)
    pghandler.finish()
    log.info('Finished with the catalog, removed a total of %d items' % removed)
    log.info("Length: %d, len(uids): %d, len(paths): %d" % (zcat._length.value,
        len(zcat.uids), len(zcat.paths)))

    transaction.commit()


def uidDuplications(self):
    pc = getToolByName(self, 'portal_catalog')
    ptool = getToolByName(self, 'portal_url')
    pghandler = ZLogHandler(1000)
    portal = ptool.getPortalObject()
    basecat = pc._catalog
    index = basecat.indexes['UID']
    size = len(index._index.keys())
    pghandler.init('Remove stale items from catalog', size)
    cnt = 0
    for uid, rid in index._index.items():
        path = basecat.paths[rid]
        pghandler.report(cnt)
        cnt += 1
        try:
            obj = portal.restrictedTraverse(path)
        except:
#            print "could not get obj for path %s, skipping" % path
           # we ignore this for the moment
            continue
        parent = aq_parent(obj)
        ids = [x['id'] for x in parent._objects]
        if obj.getId() not in ids and obj.getId() not in parent.objectIds():
            print "path %s not in parent " % path
            del index._index[uid]
            index._length.change(-1)

    return "done"


