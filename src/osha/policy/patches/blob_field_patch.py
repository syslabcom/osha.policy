# patching the index_html method of plone.app.blob's BlobField
# Reason: to disable the Accept-Ranges header
# This was causing problems with the inline Adobe Acrobat Reader
# plugin for Firefox on Windows:
# https://syslab.com/proj/issues/show/716

print "\n\nplone.app.blob.field patch"

from plone.app.blob.field import BlobField


def index_html(self, instance, REQUEST=None, RESPONSE=None, disposition='inline'):
    """ make it directly viewable when entering the objects URL """
    if REQUEST is None:
        REQUEST = instance.REQUEST
    if RESPONSE is None:
        RESPONSE = REQUEST.RESPONSE
    blob = self.getUnwrapped(instance, raw=True)    # TODO: why 'raw'?
    RESPONSE.setHeader('Last-Modified', rfc1123_date(instance._p_mtime))
    RESPONSE.setHeader('Content-Type', self.getContentType(instance))
    # The only change is to comment out this header:
    #RESPONSE.setHeader('Accept-Ranges', 'bytes')
    if handleIfModifiedSince(instance, REQUEST, RESPONSE):
        return ''
    length = blob.get_size()
    RESPONSE.setHeader('Content-Length', length)
    filename = self.getFilename(instance)
    if filename is not None:
        filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
            unicode(filename, instance.getCharset()))
        header_value = contentDispositionHeader(
            disposition=disposition,
            filename=filename)
        RESPONSE.setHeader("Content-disposition", header_value)
    range = handleRequestRange(instance, length, REQUEST, RESPONSE)
        return blob.getIterator(**range)

BlobField.index_html = index_html
