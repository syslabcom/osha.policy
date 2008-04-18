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
    """Retriever for documents with one or more RichText widgets."""

    __implements__ = (IRetriever,)

    name = "RichDocument"
    defaults = ["RichDocument"]

    def retrieveLinks(self, object):
        """Finds all links from the object and return them."""
        return retrieveAllRichTextFields(object)

    def updateLink(self, oldurl, newurl, object):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        updateAllRichTextFields(oldurl, newurl, object)

class OSHLinkRetriever(object):
    """Retriever for documents with one or more RichText widgets."""

    __implements__ = (IRetriever,)

    name = "OSHLink"
    defaults = ["OSH_Link"]

    def retrieveLinks(self, object):
        """Finds all links from the object and return them."""
        links = retrieveAllRichTextFields(object)
        links.append(object.getRemoteUrl())
        return links

    def updateLink(self, oldurl, newurl, object):
        """Replace all occurances of <oldurl> on object with <newurl>."""
        updateAllRichTextFields(oldurl, newurl, object)
        if object.getRemoteUrl() == oldurl:
            object.setRemoteUrl(newurl)


"""register retrievers"""
GlobalRegistry.register(RichDocumentRetriever())
GlobalRegistry.register(OSHLinkRetriever())
