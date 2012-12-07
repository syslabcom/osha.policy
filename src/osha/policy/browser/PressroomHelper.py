from zope.interface import implements

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.PressRoom.interfaces.content import IPressRoom

from interfaces import IPressroomHelper
from osha.policy.utils import find_parent_by_interface


class PressroomHelper(BrowserView):
    implements(IPressroomHelper)

    def getTranslatedReferences(self, fieldname=None):
        """ See interface """

        if fieldname is None:
            raise ValueError('You need to enter a field name.')

        field = self.context.getField(fieldname)
        objs = field.getAccessor(self.context)() or list()
        # Look for translated versions, but fall back
        # to original if no translation is available
        # (requires Products.LinguaPlone)
        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        return [obj.getTranslation(lang) or obj for obj in objs]

    def getContacts(self):
        """ See interface """
        press_room = find_parent_by_interface(self.context, IPressRoom)

        if press_room:
            contacts = press_room.Schema().getField(
                'contacts').getRaw(press_room)
            # If there is no contacts in the native language, use
            # contact info from canonical object
            if not contacts:
                press_room = press_room.getCanonical()
                contacts = press_room.Schema().getField(
                    'contacts').getRaw(press_room)
            return contacts
