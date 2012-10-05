from Acquisition import aq_parent, aq_inner
from Products.Archetypes.utils import shasattr
from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
from Products.LinguaPlone import config
from Products.LinguaPlone.interfaces import ILocateTranslation
from Products.LinguaPlone.interfaces import ITranslationFactory
from Products.CMFPlone.utils import _createObjectByType
from Products.LinguaPlone import events
from zope.event import notify


# Reason for this patch:
# We call unmarkCreationFlag on all translations, so that the id (short-name)
# of translations is NOT built from the title
# Osha ticket #5793

# Second reason
# We don't want to lose all translation references when an item is set to language neutral


def addTranslation(self, language, *args, **kwargs):
    """Adds a translation."""
    if self.hasTranslation(language):
        translation = self.getTranslation(language)
        raise AlreadyTranslated(translation.absolute_url())

    locator = ILocateTranslation(self)
    parent = locator.findLocationForTranslation(language)

    notify(events.ObjectWillBeTranslatedEvent(self, language))

    canonical = self.getCanonical()
    kwargs[config.KWARGS_TRANSLATION_KEY] = canonical

    factory = ITranslationFactory(self)
    translation = factory.createTranslation(
        parent, language, *args, **kwargs)
    # special handling for Belgium
    ppath = '/'.join(parent.getPhysicalPath())
    if not ppath.startswith('/osha/portal/fop/belgium'):
        translation.unmarkCreationFlag()
    translation.reindexObject()
    notify(events.ObjectTranslatedEvent(self, translation, language))

    return translation


I18NBaseObject.addTranslation = addTranslation


def setLanguage(self, value, **kwargs):
    """Sets the language code.

    When changing the language in a translated folder structure,
    we try to move the content to the existing language tree.
    """
    # If we are called during a schema update we should not be
    # deleting any language relations or complaining about already
    # existing translations.  A schema update saves the current
    # value, sets the default language (at which point there can
    # easily be two English translations if that is the default
    # language) and restores the original value again.  So really
    # there is no reason for doing anything other than setting the
    # value.
    req = getattr(self, 'REQUEST', None)
    if shasattr(req, 'get'):
        if req.get('SCHEMA_UPDATE', None) is not None:
            # We at least should set the field.
            self.getField('language').set(self, value, **kwargs)
            return

    translation = self.getTranslation(value)
    if self.hasTranslation(value):
        if translation == self:
            return
        else:
            raise AlreadyTranslated(translation.absolute_url())
    self.getField('language').set(self, value, **kwargs)

    # THIS IS THE PATCH
    # we don't kill all references when an item is set to neutral
####     if not value:
####        self.deleteReferences(RELATIONSHIP)

    parent = aq_parent(aq_inner(self))

    locator = ILocateTranslation(self)
    new_parent = locator.findLocationForTranslation(value)

    if new_parent != parent:
        info = parent.manage_cutObjects([self.getId()])
        new_parent.manage_pasteObjects(info)
    self.reindexObject()
    self._catalogRefs(self)

I18NBaseObject.setLanguage = setLanguage
