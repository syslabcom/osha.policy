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

    def getNotes(self):
        notes = self.getTranslatedReferences(fieldname='notesToEditors')
        texts = [note.getText() for note in notes]
        # insert number here...
        for i in range(len(texts)):
            soup = BeautifulSoup(texts[i])
            pTag = soup.p
            if not pTag:
                # can't don anything, continue
                continue
            substr = pTag.contents[0].string
            pTag.contents[0] = NavigableString(u'<span class="numbering">%d.</span> ' % (i + 1) + substr)
            texts[i] = str(soup)
        return texts

    def getContacts(self):
        """ See interface """
        pressroom = find_parent_by_interface(self.context, IPressRoom)

        if not pressroom:
            raise KeyError('No Press Room found!')

        # if showContacts is set to False return None
        show_contacts = self.context.getField('showContacts')
        if show_contacts and not show_contacts.getAccessor(self.context)():
            return None

        language_tool = getToolByName(self.context, 'portal_languages')
        lang = language_tool.getPreferredLanguage()
        pressroom_trans = pressroom.getTranslation(lang)
        contacts_trans = (pressroom_trans and
            pressroom_trans.getField('contacts').getRaw(pressroom_trans))
        contacts = pressroom.getField('contacts').getRaw(pressroom)

        return contacts_trans or contacts
