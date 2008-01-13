from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Acquisition import aq_parent, aq_inner
from Products.LinguaPlone.interfaces import ITranslatable
from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
from Products.LinguaPlone import config
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import isDefaultPage
from plone.locking.interfaces import ILockable

# Reason for this patch:
# Currently, LP assumes the mutator is defined on the object (only).
#
# When using schemaextender however, accessors and mutators for ExtensionFields are not 
# available on the object. See the following posting: http://www.nabble.com/ANN:-[…]er-1.0a1-t4626771s6741.html
#
# Therefore I propose for LP to look at the field itself to get the mutator, in case it is not 
# found on the object. That way, the mutator can be defined on the ExtensionField directly.

# This patch was proposed to the LP Issue tracker: http://plone.org/products/linguaplone/issues/116

def addTranslation(self, language, *args, **kwargs):
    """Adds a translation."""
    canonical = self.getCanonical()
    parent = aq_parent(aq_inner(self))
    if ITranslatable.providedBy(parent):
        parent = parent.getTranslation(language) or parent
    if self.hasTranslation(language):
        translation = self.getTranslation(language)
        raise AlreadyTranslated, translation.absolute_url()
    id = canonical.getId()
    while not parent.checkIdAvailable(id):
        id = '%s-%s' % (id, language)
    kwargs[config.KWARGS_TRANSLATION_KEY] = canonical
    if kwargs.get('language', None) != language:
        kwargs['language'] = language
    o = _createObjectByType(self.portal_type, parent, id, *args, **kwargs)
    # If there is a custom factory method that doesn't add the
    # translation relationship, make sure it is done now.
    if o.getCanonical() != canonical:
        o.addTranslationReference(canonical)
    self.invalidateTranslationCache()
    # Copy over the language independent fields
    schema = canonical.Schema()
    independent_fields = schema.filterFields(languageIndependent=True)
    for field in independent_fields:
        accessor = field.getEditAccessor(canonical)
        if not accessor:
            accessor = field.getAccessor(canonical)
        data = accessor()
        # PATCH BEGINS HERE
        translation_mutator = getattr(o, field.translation_mutator, None)
        if not translation_mutator:
            translation_mutator = getattr(field, field.translation_mutator)
        # PATCH ENDS HERE
        translation_mutator(data)
    # If this is a folder, move translated subobjects aswell.
    if self.isPrincipiaFolderish:
        moveids = []
        for obj in self.objectValues():
            if ITranslatable.providedBy(obj) and \
                       obj.getLanguage() == language:
                lockable = ILockable(obj, None)
                if lockable is not None and lockable.can_safely_unlock():
                    lockable.unlock()
                moveids.append(obj.getId())
        if moveids:
            o.manage_pasteObjects(self.manage_cutObjects(moveids))
    o.reindexObject()
    if isDefaultPage(canonical, self.REQUEST):
        o._lp_default_page = True


I18NBaseObject.addTranslation = addTranslation