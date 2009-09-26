from Products.PlacelessTranslationService import getTranslationService

class PrettyFormatter(object):
    
    def __init__(self, context):
        self.context = context
        self.pts = getTranslationService()
    
    def formatKeyword(self, kw):
        kw = self.pts.translate(domain="osha", msgid=kw, context=self.context)
        return kw