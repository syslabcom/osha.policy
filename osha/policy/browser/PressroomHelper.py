from interfaces import IPressroomHelper
from Products.CMFCore.utils import getToolByName
from zope.interface import implements
from Products.CMFPlone import utils
from Products.Five import BrowserView
try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    HAS_LINGUAPLONE = False
else:
    HAS_LINGUAPLONE = True



class PressroomHelper(BrowserView):
    implements(IPressroomHelper)

    def getTextPieces(self):
        """ See interface """
        textpieces = list()
        field = self.context.getField('referenced_content')
        objs = field.getAccessor(self.context)()
        # If LinguaPlone is present, look for translated versions, but fall back
        #  to original if no translation is available
        if HAS_LINGUAPLONE:
            language_tool = getToolByName(self.context, 'portal_languages')
            lang = language_tool.getPreferredLanguage()
            objs = [obj.getTranslation(lang) or obj for obj in objs]
        for obj in objs:
            textpieces.append(obj.getText())

        return textpieces