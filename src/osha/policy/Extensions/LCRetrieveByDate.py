import transaction
import zLOG
from DateTime import DateTime
from slc.outdated import ANNOTATION_KEY
from zope.annotation.interfaces import IAnnotatable, IAnnotations

ALLOWED_STATES = ['undefined', 'published', 'visible', 'to_amend']


def LCRetrieveByDate(self, skiplist=[]):
    """Retrieves the links from all objects in the site by Date."""
    sincedate = DateTime()-6*30
    since = self.REQUEST.get('since')
    if since is not None:
        since = DateTime(since)
    sincedate = since or sincedate

    pwt = self.portal_workflow
    lc = self.portal_linkchecker
    server = lc.database._getWebServiceConnection()
    if server is None:
        raise RuntimeError, "The site could not be crawled because no " \
                            "connection to the lms could be established."


#    # Not actually necessary on every crawl, but it doesn't seem to work
#    # in the installer, so this seems the next logical place to do it.
#    self.portal_catalog.reindexIndex('portal_linkchecker_uid', self.REQUEST)
    if 1:
        # gather all objects that are of a type we can check for links
        objects = self.portal_catalog(Language='all', modified={'query':sincedate,'range':'min'})
        os_ = len(objects)
        zLOG.LOG('CMFLinkChecker', zLOG.INFO, "%d objects will be crawled" % os_)
        i = 0
        for ob in objects:
            i += 1
            zLOG.LOG("CMFLinkChecker", zLOG.BLATHER,
                     "Site Crawl Status",
                     "%s of %s (%s)" % (i, os_, ob.getPath()))
            ob = ob.getObject()
            if ob is None:
                # Maybe the catalog isn't up to date
                continue
            outdated = IAnnotatable.providedBy(ob) and \
                IAnnotations(ob).get(ANNOTATION_KEY, False) or False
            if outdated:
                zLOG.LOG("CMFLinkChecker", zLOG.BLATHER, "unregistering, object is outdated")
                lc.database.unregisterObject(ob)
                continue
            try:
                state = pwt.getInfoFor(ob, 'review_state')
            except:
                state = "undefined"
            if state not in ALLOWED_STATES:
                zLOG.LOG("CMFLinkChecker", zLOG.BLATHER, "unregistering, object is not public: %s" % state)
                lc.database.unregisterObject(ob)
                continue
            try:
                lc.retrieving.retrieveObject(ob, online=False)
            except Exception,e:
                zLOG.LOG('CMFLinkChecker', zLOG.BLATHER,
                  "Unable to retrieveObject for %s. Error: %s" %([ob], e))
            if not i % 500 :
                transaction.savepoint()
                zLOG.LOG('CMFLinkChecker', zLOG.INFO,
                    "Crawling site - commited after %d objects" %(i))
    return "finished"
