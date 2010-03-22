import transaction
import zLOG
from DateTime import DateTime

def LCRetrieveByDate(self, skiplist=[]):
    """Retrieves the links from all objects in the site by Date."""
    sincedate = DateTime()-6*30
    since = self.REQUEST.get('since')
    if since is not None:
        since = DateTime(since)
    sincedate = since or sincedate
    
    lc = self.portal_linkchecker
    server = lc.database._getWebServiceConnection()
    if server is None:
        raise RuntimeError, "The site could not be crawled because no " \
                            "connection to the lms could be established."
    #server.setClientNotifications(False)

#    # Not actually necessary on every crawl, but it doesn't seem to work
#    # in the installer, so this seems the next logical place to do it.
#    self.portal_catalog.reindexIndex('portal_linkchecker_uid', self.REQUEST)
    try:
        database = lc.database
        # gather all objects that are of a type we can check for links
        if 1:
        #for type in lc.retrieving.listSupportedTypes():
            objects = self.portal_catalog(Language='all', modified={'query':sincedate,'range':'min'})
            os_ = len(objects)
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
                #try:
                lc.retrieving.retrieveObject(ob, online=False)
                #except Exception,e:
                #    zLOG.LOG('CMFLinkChecker', zLOG.INFO,
                #      "Unable to retrieveObject for %s. Error: %s" %([ob], e))
                if not i % 500 :
                    transaction.savepoint()
                    zLOG.LOG('CMFLinkChecker', zLOG.INFO,
                        "Crawling site - commited after %d objects of type %s" %(i, type))
    finally:
        pass
        #server.setClientNotifications(True)

