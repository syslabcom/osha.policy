from zope.i18n import translate

class PrettyFormatter(object):
    
    def __init__(self, context):
        self.context = context
    
    def formatKeyword(self, kw):
        kw = translate(kw, domain="osha")
        return kw