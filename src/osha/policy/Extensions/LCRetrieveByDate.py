import transaction
import zLOG
from DateTime import DateTime
from slc.outdated import ANNOTATION_KEY
from zope.annotation.interfaces import IAnnotatable, IAnnotations
from plone.app.async.interfaces import IAsyncService
from zope.component import getUtility
from Products.Archetypes.interfaces import IReferenceable
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from osha.policy.handlers import job_failure_callback, retrieve_async, unregister_async

ALLOWED_STATES = ['undefined', 'published', 'visible', 'to_amend']


def LCRetrieveByDate(self, skiplist=[]):
    """Retrieves the links from all objects in the site by Date."""
    sincedate = DateTime()-6*30
    since = self.REQUEST.get('since')
    if since is not None:
        since = DateTime(since)
    sincedate = since or sincedate
    offline = self.REQUEST.get('offline', '')

    pwt = self.portal_workflow
    lc = self.portal_linkchecker
    async = getUtility(IAsyncService)
    sm = getSecurityManager()
    try:
        server = lc.database._getWebServiceConnection()
    except:
        server = None
    if server is None and offline!='1':
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
        for res in objects:
            i += 1
            zLOG.LOG("CMFLinkChecker", zLOG.BLATHER,
                     "Site Crawl Status",
                     "%s of %s (%s)" % (i, os_, res.getPath()))
            ob = res.getObject()
            if ob is None:
                # Maybe the catalog isn't up to date
                continue
            outdated = IAnnotatable.providedBy(ob) and \
                IAnnotations(ob).get(ANNOTATION_KEY, False) or False
            if outdated:
                zLOG.LOG("CMFLinkChecker", zLOG.INFO, "unregistering %s, object is outdated" % res.getPath())
                links = lc.database.getLinksForObject(ob)
                link_ids = [x.getId() for x in links]
                job = async.queueJob(unregister_async, lc, link_ids)
                callback = job.addCallbacks(failure=job_failure_callback)
                continue
            try:
                state = pwt.getInfoFor(ob, 'review_state')
            except:
                state = "undefined"
            if state not in ALLOWED_STATES:
                zLOG.LOG("CMFLinkChecker", zLOG.BLATHER, "unregistering, object is not public: %s" % state)
                links = lc.database.getLinksForObject(ob)
                link_ids = [x.getId() for x in links]
                job = async.queueJob(unregister_async, lc, link_ids)
                callback = job.addCallbacks(failure=job_failure_callback)
                continue
            if not sm.checkPermission(ModifyPortalContent, ob):
                continue
            if (not IReferenceable.providedBy(ob)):
                continue
            job = async.queueJob(retrieve_async, ob, res.getPath(), online=False)
            callback = job.addCallbacks(failure=job_failure_callback)
            if not i % 500 :
                transaction.savepoint()
                zLOG.LOG('CMFLinkChecker', zLOG.INFO,
                    "Crawling site - commited after %d objects" %(i))
    return "finished"
