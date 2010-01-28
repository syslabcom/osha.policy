# patching the index_html method of plone.app.blob's content type
# Reason: ATFile.inlineMimetypes does not include "text/html",
# but we need it in there

print "\n\nplone.app.blob patch"

from plone.app.blob.content import ATBlob
from plone.app.blob.interfaces import IATBlobImage
from Products.ATContentTypes.content.file import ATFile

def index_html(self, REQUEST, RESPONSE):
    """ download the file inline or as an attachment """
    field = self.getPrimaryField()
    inlineMimetypes = [x for x in ATFile.inlineMimetypes]
    if "text/html" not in inlineMimetypes:
        inlineMimetypes.append("text/html")

    if IATBlobImage.providedBy(self):
        return field.index_html(self, REQUEST, RESPONSE)
    elif field.getContentType(self) in inlineMimetypes:
        return field.index_html(self, REQUEST, RESPONSE)
    else:
        return field.download(self, REQUEST, RESPONSE)

ATBlob.index_html = index_html
