from zope.i18n import translate
from Products.CMFCore.utils import getToolByName

class PrettyFormatter(object):
    
    def __init__(self, context):
        self.context = context
    
    def formatKeyword(self, kw):
        lang = getToolByName(self.context, 'portal_languages').getPreferredLanguage()
        kw = translate(domain="osha", msgid=kw, target_language=lang)
        return kw