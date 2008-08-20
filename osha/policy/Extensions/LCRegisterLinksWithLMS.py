import transaction
from Products.CMFCore.utils import getToolByName
from gocept.linkchecker.database import WEBSERVICE_STATEMAP
import gocept.linkchecker.utils

def registerLinks(self, threshold=100):
    try: threshold = int(threshold)
    except: threshold = 100
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
        print "I have %d unregistered links. Processing the first %d" %(len(unregistered), threshold)
        subset = unregistered[:threshold]
        unregistered= unregistered[threshold:]
        states = lms.registerManyLinks(subset)
        for url, state, reason in states:
            state = WEBSERVICE_STATEMAP[state]
            url = lc.database[gocept.linkchecker.utils.hash_url(url)]
            url.registered = True
            url.updateStatus(state, reason)

    return "processed a total of %d links" %total