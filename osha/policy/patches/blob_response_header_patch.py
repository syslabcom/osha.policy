# this patch inserts the response header "Content-Type" so that blob files can be downloaded correctly
# This has been filed as bug #
# remove if fixed by plone.app.blob

from plone.app.blob.field import BlobField
from plone.app.blob.content import ATBlob
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from Products.Archetypes.utils import contentDispositionHeader
from webdav.common import rfc1123_date

def field_index_html(self, instance, REQUEST=None, RESPONSE=None, disposition='inline'):
    """ make it directly viewable when entering the objects URL """
    if REQUEST is None:
        REQUEST = instance.REQUEST
    if RESPONSE is None:
        RESPONSE = REQUEST.RESPONSE
    filename = self.getFilename(instance)
    if filename is not None:
        filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
            unicode(filename, instance.getCharset()))
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
    return field.index_html(self, REQUEST, RESPONSE)
                
BlobField.index_html = field_index_html        
ATBlob.index_html = file_index_html