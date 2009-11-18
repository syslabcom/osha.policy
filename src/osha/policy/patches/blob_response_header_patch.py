# this patch inserts the response header "Content-Type" so that blob files can be downloaded correctly
# This has been filed as bug #
# remove if fixed by plone.app.blob

from plone.app.blob.field import BlobField
from plone.app.blob.content import ATBlob
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from Products.Archetypes.utils import contentDispositionHeader
from webdav.common import rfc1123_date
from Products.ATContentTypes.content.file import ATFile


def field_index_html(self, instance, REQUEST=None, RESPONSE=None, disposition='inline'):
    """ make it directly viewable when entering the objects URL """
    if REQUEST is None:
        REQUEST = instance.REQUEST
    if RESPONSE is None:
        RESPONSE = REQUEST.RESPONSE
    filename = self.getFilename(instance)
    if filename is not None:
        try:
            filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
                unicode(filename, instance.getCharset()))
        except TypeError:
            pass #Then, use the normal one
        header_value = contentDispositionHeader(
            disposition=disposition,
            filename=filename)
        RESPONSE.setHeader("Content-disposition", header_value)
    blob = self.get(instance, raw=True)     # TODO: why 'raw'?
    RESPONSE.setHeader('Last-Modified', rfc1123_date(instance._p_mtime))
    RESPONSE.setHeader('Content-Type', instance.content_type)
    RESPONSE.setHeader("Content-Length", blob.get_size())
    return blob.getIterator()
        
        
        
def file_index_html(self, REQUEST, RESPONSE):
    """ download the file inline """
    
    field = self.getPrimaryField()
    # Careful, inline Mimetypes does not contain text/html or text/plain
    # For Old Campaign sides sake we add that as well.
    inlineMimetypes = ATFile.inlineMimetypes + ('text/html', 'text/plain')

    # Return everything inline and let the browser determine what to present as download
    return field.index_html(self, REQUEST, RESPONSE)
#    if field.getContentType(self) in inlineMimetypes:
#        # return the PDF and Office file formats inline
#        return field.index_html(self, REQUEST, RESPONSE)
#    return field.download(self, REQUEST, RESPONSE)
                
BlobField.index_html = field_index_html        
ATBlob.index_html = file_index_html
