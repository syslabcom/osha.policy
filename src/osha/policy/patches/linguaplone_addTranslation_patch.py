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
    translation.unmarkCreationFlag()
    translation.reindexObject()
    notify(events.ObjectTranslatedEvent(self, translation, language))

    return translation


I18NBaseObject.addTranslation = addTranslation
