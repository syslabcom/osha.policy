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
    
    unregistered = [url.url for url in unregistered]
    total = len(unregistered)
    while len(unregistered):
        log.info( "\nI have %d unregistered links. Processing the first %d" %(len(unregistered), threshold))

        subset = unregistered[:threshold]
        unregistered = unregistered[threshold:]
        states = lms.registerManyLinks(subset)
#        import pdb; pdb.set_trace()
        log.info("%d states were returned by the lms" %len(states))
        for url, state, reason in states:
            state = WEBSERVICE_STATEMAP[state]
            url = lc.database[gocept.linkchecker.utils.hash_url(url)]
            url.registered = True
            url.updateStatus(state, reason)
        log.info("Committing, will now sleep fo a while...")
        time.sleep(120)

    msg = "processed a total of %d links" % total
    log.info(msg)
    return msg