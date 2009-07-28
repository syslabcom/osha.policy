from Products.QueueCatalog import QueueCatalog

def getMetadataForUID(self, uid):
    """return the correct metadata given the uid, usually the path"""
    return self.getZCatalog().getMetadataForUID(uid)

QueueCatalog.getMetadataForUID = getMetadataForUID
