from Products.PressRoom.content.PressRelease import schema as PressReleaseSchema
from Products.PressRoom.content.PressRelease import PressRelease

###
# Moved to osha.adaptation.schema.PressReleaseModifier
###

# PressReleaseSchema['subhead'].languageIndependent = False
# PressReleaseSchema['releaseDate'].languageIndependent = True
# PressReleaseSchema['releaseContacts'].languageIndependent = True

def Date(self):
    """Avoid the need for a getStoryDate metadatum in the catalog"""
    return self.getStorydate()

PressRelease.Date = Date