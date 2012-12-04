from Products.PressRoom.content.PressRelease import PressRelease


def Date(self):
    """Avoid the need for a getStoryDate metadatum in the catalog"""
    return self.getStorydate()

PressRelease.Date = Date
