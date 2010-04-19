from gocept.linkchecker import link, utils, database, url
import gocept.linkchecker.interfaces
import gocept.linkchecker.utils
from gocept.linkchecker.database import WEBSERVICE_STATEMAP

import zLOG
from Products.CMFCore.utils import getToolByName
from urlparse import urlparse, urlunparse, urljoin
from DateTime import DateTime

zLOG.LOG('gocept.linkchecker', zLOG.INFO, 'Patching Linkchecker')

def getURL(self):         
    """Return the URL object this link refers to."""        
    lc = getToolByName(self, "portal_linkchecker")
    res = lc.database.queryURLs(url=self.url)
    # Coping with links present in lms but not in linkchecker
    if not res:
       zLOG.LOG('gocept.linkchecker', zLOG.ERROR, 'URL not found in catalog: %s' % self.url)
       return None
    return lc.database.queryURLs(url=self.url)[0].getObject()
    
    
def index(self):
    self.url = gocept.linkchecker.utils.resolveRelativeLink(self.link, self.getObject())
    url = self.getURL()
    # Coping with links present in lms but not in linkchecker
    if not url:
        return None
    self.state = url.state
    self.reason = url.reason
    self.lastcheck = url.lastcheck
    path = '/'.join(self.getPhysicalPath())
    self.link_catalog.catalog_object(self, path)
        

def resolveRelativeLink(url, context):
    """Normalizes a URL according to RfC 2396 and throws away the fragment
    component, if any.
    """
    url_ = utils.urlrecord(url)

    if url_.scheme:
        # Url has a protocol specified, e.g. HTTP, so we need not complete it.
        # We're only interested in a few protocols, though.
        if url_.scheme.lower() not in ['http', 'https', 'ftp']:
            return url
    elif url_.netloc:
        # A host is given, so we assume the HTTP protocol.
        url_.scheme = 'http'
    else:
        # We only have a path. We join it with the configured prefix (or use the
        # request if nothing was specified).
        try:
            lc = getToolByName(context, "portal_linkchecker")
        except Exception, e:
            return ''
        prefix = lc.database.defaultURLPrefix or context.REQUEST.BASE0
        if prefix.endswith('/'):
            prefix = prefix[:-1]
        # this mechanism does not honor virtual hosting
        #prefix += '/'.join(context.getPhysicalPath())
        portal_url = getToolByName(context, 'portal_url')
        prefix += '/'+portal_url.getRelativeContentURL(context)

        # Make up for a deviation of Python's urljoin from the test cases given
        # in RfC 2396, Appendix C.
        if url.startswith('?'):
            url = './' + url

        url = urljoin(prefix, url)
        url_ = utils.urlrecord(url)

    url_.scheme = url_.scheme.lower()
    url_.netloc = url_.netloc.lower()

    if ':' in url_.netloc:
        hostname, port = url_.netloc.split(':')
        if port == str(utils.inet_services.get(url_.scheme)):
            url_.netloc = hostname

    if not url_.path:
        url_.path = '/'

    url_.fragment = ''

    new_url = str(url_)
    return new_url


def _register_urls_at_lms(self, url_objects):
    """Register the given URL objects at the LMS web service.
    """
    # Do we have an LMS connection?
    print "PATCHED _register_urls_at_lms"
    lms = self._getWebServiceConnection()
    if lms is None:
        return
    urls = [url.url for url in url_objects]
    states = lms.registerManyLinks(urls)
    # The server *may* report the status of URls it already knows.
    for url, state, reason in states:
        state = WEBSERVICE_STATEMAP[state]
        # don't fail if the url object is missing due to inconsistencies of
        # the database
        try:
            url = self[gocept.linkchecker.utils.hash_url(url)]
        except:
            continue
        url.updateStatus(state, reason)
    # Mark all of the URLs as registered
    for url in url_objects:
        if not url.registered:
            url.registered = True
            # update the url_catalog about the status
            url.index()


def updateStatus(self, state, reason):
    assert state in ['red', 'green', 'orange', 'grey'], \
        "Invalid state %s" % state
    self.reason = reason
    now = DateTime()
    if state != self.state:
        self.laststate = self.state
        self.state = state
        self.lastupdate = now
    # here patched: always set the lastchecked param
    self.lastcheck = now
    self.index()
    # Reindex link objects to update their status caches
    for link in self.getLinks():
        link.index()


link.Link.getURL = getURL
link.Link.index = index        
utils.resolveRelativeLink = resolveRelativeLink
database.LinkDatabase._register_urls_at_lms = _register_urls_at_lms
url.URL.updateStatus = updateStatus
