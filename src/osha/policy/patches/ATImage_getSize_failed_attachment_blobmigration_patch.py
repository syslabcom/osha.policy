from Products.ATContentTypes.content.image import ATImage
from plone.app.blob.field import BlobField


# The migration to blobstrage on SimpleAttachments has failed.
# That means we have a co-existance of ImageFields that are blobs,
# and others that are zope Images
# getSize() behaves differently for both cases
# Of course we need to be aware that we will return bogus valus for height and width for 
# the failed ImageAttachments

def getWidth(self, scale=None):
    size = self.getSize(scale)
    if isinstance(size, int):
        return size
    return size[0]

def getHeight(self, scale=None):
    size = self.getSize(scale)
    if isinstance(size, int):
        return size
    return size[1]

ATImage.getWidth = getWidth
ATImage.getHeight = getHeight


# Apparently SimpleAttachment assumes we already have blobs. Of course
# some stuff does not work therefore.

def getFilename(self, instance, fromBaseUnit=True):
    """ return the file name associated with the blob data """
    blob = self.getUnwrapped(instance)
    if blob is not None:
        # we not actually be a blob....
        func = getattr(blob, 'getFilename', None)
        if func:
            return blob.getFilename()
        else:
            return blob.filename
    else:
        return None

BlobField.getFilename = getFilename

