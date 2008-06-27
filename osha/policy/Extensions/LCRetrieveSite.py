
import transaction
import zLOG

def LCRetrieveSite(self):
    """Retrieves the links from all objects in the site."""
    lc = self.portal_linkchecker
    server = lc.database._getWebServiceConnection()
    if server is None:
        raise RuntimeError, "The site could not be crawled because no " \
                            "connection to the lms could be established."
    server.setClientNotifications(False)

#    # Not actually necessary on every crawl, but it doesn't seem to work
#    # in the installer, so this seems the next logical place to do it.
#    self.portal_catalog.reindexIndex('portal_linkchecker_uid', self.REQUEST)
    try:
        database = lc.database
        # gather all objects that are of a type we can check for links
        for type in lc.retrieving.listSupportedTypes():
            objects = self.portal_catalog(portal_type=type, Language='all')
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
                try:
                    lc.retrieving.retrieveObject(ob)
                except Exception,e:
                    zLOG.LOG('CMFLinkChecker', zLOG.INFO,
                      "Unable to retrieveObject for %s. Error: %s" %([ob], e))
                if i % 1000 ==0:
                    transaction.commit()
                    zLOG.LOG('CMFLinkChecker', zLOG.INFO,
                        "Crawling site - commited after %d objects of type %s" %(i, type))
            transaction.commit()
        # Remove unused urls
        database.cleanup()
    finally:
        server.setClientNotifications(True)
 