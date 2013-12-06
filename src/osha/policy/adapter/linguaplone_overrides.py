from Acquisition import (
    aq_inner,
    aq_parent,
)
from Products.CMFPlone.utils import _createObjectByType
from Products.LinguaPlone.utils import (
    TranslationFactory,
    LanguageIndependentFields,
)
from Products.LinguaPlone.interfaces import (
    ITranslationFactory,
    ITranslatable,
)
from plone.app.layout.navigation.defaultpage import isDefaultPage
from plone.locking.interfaces import ILockable
from osha.policy.interfaces import IOSHATranslatable
from zope.component import adapts
from zope.interface import implements

"""
Reason for Overwriting the translation factory:
When a new translation is created, the copyFields method is called for all
language-independent fields. However, the values from the canonical are not
only copied to the new translation, but to ALL existing translations.
With a large image (e.g. on a News Item) this can cause massive performance
problems.

Therefore, when a translation is created, use our custom
OSHALanguageIndependentFields adapter, to set field values directly on the
translation without calling the mutator.
"""


class OSHATranslationFactory(TranslationFactory):
    """OSHA translation factory.
    """

    implements(ITranslationFactory)
    adapts(IOSHATranslatable)

    def createTranslation(self, container, language, *args, **kwargs):
        context = aq_inner(self.context)
        canonical = context.getCanonical()
        portal_type = self.getTranslationPortalType(container, language)
        new_id = kwargs.pop(
            'id', self.generateId(container, canonical.getId(), language))
        kwargs["language"] = language
        translation = _createObjectByType(portal_type, container,
                                          new_id, *args, **kwargs)

        # If there is a custom factory method that doesn't add the
        # translation relationship, make sure it is done now.
        if translation.getCanonical() != canonical:
            translation.addTranslationReference(canonical)

        # THIS IS THE LINE WE NEED TO CUSTOMIZE
        OSHALanguageIndependentFields(canonical).copyFields(translation)

        if isDefaultPage(aq_parent(aq_inner(canonical)), canonical):
            translation._lp_default_page = True

        # If this is a folder, move translated subobjects aswell.
        if context.isPrincipiaFolderish:
            moveids = []
            for obj in context.values():
                translator = ITranslatable(obj, None)
                if translator is not None \
                   and translator.getLanguage() == language:
                    lockable = ILockable(obj, None)
                    if lockable is not None and lockable.can_safely_unlock():
                        lockable.unlock()
                    moveids.append(obj.getId())
            if moveids:
                info = context.manage_cutObjects(moveids)
                translation.manage_pasteObjects(info)

        return translation


class OSHALanguageIndependentFields(LanguageIndependentFields):

    def copyField(self, field, translation):
        accessor = field.getEditAccessor(self.context)
        if not accessor:
            accessor = field.getAccessor(self.context)
        if accessor:
            data = accessor()
        else:
            data = field.get(self.context)
        # Screw the mutator, just set the value on exactly this field of
        # exactly this item
        field.set(translation, data)
