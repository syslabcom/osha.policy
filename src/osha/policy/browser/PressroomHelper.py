from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.PressRoom.interfaces.content import IPressRoom

from interfaces import IPressroomHelper
from osha.policy.utils import find_parent_by_interface


class PressroomHelper(BrowserView):
    implements(IPressroomHelper)

    def getTextPieces(self):
        """ See interface """
        textpieces = list()
        field = self.context.getField('referenced_content')
        objs = field.getAccessor(self.context)() or list()
        # Look for translated versions, but fall back
        # to original if no translation is available
        # (requires Products.LinguaPlone)
        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        objs = [obj.getTranslation(lang) or obj for obj in objs]
        for obj in objs:
            textpieces.append(obj.getText())

        return textpieces

    def getContacts(self):
        """ See interface """
        press_room = find_parent_by_interface(self.context, IPressRoom)

        if press_room:
            return press_room.Schema().getField('contacts').getRaw(press_room)
        else:
            return ''
