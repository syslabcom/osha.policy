import transaction
from Products.CMFCore.utils import getToolByName
from gocept.linkchecker.database import WEBSERVICE_STATEMAP
import gocept.linkchecker.utils
import time
import logging
log = logging.getLogger('osha.policy.LC')

def registerLinks(self, threshold=1000):
    try: threshold = int(threshold)
    except: threshold = 1000
    lc = getToolByName(self, 'portal_linkchecker')
    unregistered = lc.database.queryURLs(registered=False)
    # Nothing to do?
    if not unregistered:
        print "no unregistered links"
        return "no unregistered links"
    # Do we have an LMS connection?
    lms = lc.database._getWebServiceConnection()
    if lms is None:
        print "no lms connection"
        return "no lms connection"
    
    urls = [url.url for url in unregistered]
    total = len(urls)
    while len(unregistered):
        log.info( "\nI have %d unregistered links. Processing the first %d" %(len(unregistered), threshold))

        subset_urls = urls[:threshold]
        subset_unregistered = unregistered[:threshold]
        unregistered = unregistered[threshold:]
        urls = urls[threshold:]
        states = lms.registerManyLinks(subset_urls)
        log.info("%d states were returned by the lms" %len(states))
        for url, state, reason in states:
            state = WEBSERVICE_STATEMAP[state]
            url = lc.database[gocept.linkchecker.utils.hash_url(url)]
            url.registered = True
            url.updateStatus(state, reason)
        # now make extra sure and mark the URL objects as registered, no matter what!
        for brain in subset_unregistered:
            url = brain.getObject()
            url.registered = True
            url.reindexObject()
        log.info("Committing, will now sleep fo a while...")
        transaction.commit()
#        time.sleep(120)

    msg = "processed a total of %d links" % total
    log.info(msg)
    return msg