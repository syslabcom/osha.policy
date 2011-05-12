from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView

from interfaces import IPressroomHelper

class PressroomHelper(BrowserView):
    implements(IPressroomHelper)

    def getTextPieces(self):
        """ See interface """
        textpieces = list()
        field = self.context.getField('referenced_content')
        objs = field.getAccessor(self.context)()
        # Look for translated versions, but fall back
        # to original if no translation is available 
        # (requires Products.LinguaPlone)
        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        objs = [obj.getTranslation(lang) or obj for obj in objs]
        for obj in objs:
            textpieces.append(obj.getText())

        return textpieces
