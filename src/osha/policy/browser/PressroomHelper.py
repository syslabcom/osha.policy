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

        if not field:
            raise KeyError('No field with %s found!' % fieldname)

        objs = field.getAccessor(self.context)() or list()
        # Look for translated versions, but fall back
        # to original if no translation is available
        # (requires Products.LinguaPlone)
        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        return [obj.getTranslation(lang) or obj for obj in objs]

    def getContacts(self):
        """ See interface """
        pressroom = find_parent_by_interface(self.context, IPressRoom)

        if not pressroom:
            raise KeyError('No Press Room found!')

        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        pressroom_trans = pressroom.getTranslation(lang)
        contacts_trans = (pressroom_trans and
            pressroom_trans.getField('contacts').getRaw(pressroom_trans))
        contacts = pressroom.getField('contacts').getRaw(pressroom)

        return contacts_trans or contacts
