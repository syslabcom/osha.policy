from gocept.linkchecker import link

import zLOG
from Products.CMFCore.utils import getToolByName

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
        
        
link.getURL = getURL
link.index = index        

