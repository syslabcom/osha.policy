from Products.CMFLinkChecker.interfaces import IRetriever
from Products.CMFLinkChecker.retrievemanager import GlobalRegistry
from Products.CMFLinkChecker.utils import retrieveHTML, retrieveSTX, \
     retrieveAllRichTextFields, updateAllRichTextFields
import urllib

def _makesafe_urls(urls):
    URLS = []
    for url in urls:
        if len(url)>255:
            continue
        try:
            unicode(url, 'ascii')
        except:
            # chars >128 in url :-?
            newstr = []
            for i in range(len(url)):
                if ord(url[i])>127:
                    newstr.append(urllib.quote(url[i]))
                else:
                    newstr.append(url[i])
            url = "".join(newstr)
        if url.strip():
            URLS.append(url)
    return URLS

class RichDocumentRetriever(object):
    """Retriever for documents with one or more RichText widgets.

        >>> _ = self.folder.invokeFactory('RichDocument', 'myrichdoc')
        >>> myob = getattr(self.folder, 'myrichdoc')
        >>> myob.setText('This is <a href="google.com">a link</a>.')
        >>> retrieve_manager = self.portal.portal_linkchecker.retrieving
        >>> retriever = retrieve_manager._getRetrieverForObject(myob)
        >>> links = retriever.retrieveLinks(myob)
        >>> 'google.com' in links
        True        
    
    """

    __implements__ = (IRetriever,)

    name = "RichDocument"
    defaults = ["RichDocument"]

    def retrieveLinks(self, object):
        """Finds all links from the object and return them."""
        return retrieveAllRichTextFields(object)

    def updateLink(self, oldurl, newurl, object):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        updateAllRichTextFields(oldurl, newurl, object)

GlobalRegistry.register(RichDocumentRetriever())
