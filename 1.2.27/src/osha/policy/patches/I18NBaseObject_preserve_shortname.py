from Products.LinguaPlone.I18NBaseObject import I18NBaseObject
from Products.Archetypes.public import *
from Products.LinguaPlone import config
from Products.LinguaPlone.interfaces import ITranslatable
from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from Products.Archetypes.utils import shasattr
from Acquisition import aq_parent, aq_inner, aq_base

def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
    """Process the schema looking for data in the form."""
    is_new_object = self.checkCreationFlag()
    
    BaseObject.processForm(self, data, metadata, REQUEST, values)
    if config.AUTO_NOTIFY_CANONICAL_UPDATE:
        if self.isCanonical():
            self.invalidateTranslations()

    if self._at_rename_after_creation and is_new_object:
        new_id = self._renameAfterCreation(check_auto_id=not not self.REQUEST.form.get('id'))
    else:
        new_id = None

    if shasattr(self, '_lp_default_page'):
        delattr(self, '_lp_default_page')
        language = self.getLanguage()
        canonical = self.getCanonical()
        parent = aq_parent(aq_inner(self))
        if ITranslatable.providedBy(parent):
            if not parent.hasTranslation(language):
                parent.addTranslation(language)
                translation_parent = parent.getTranslation(language)
                translation_parent.processForm(
                        values=dict(title=self.Title()))
                translation_parent.setDescription(self.Description())
                parent = translation_parent

            if ISelectableBrowserDefault.providedBy(parent) and new_id:
                parent.setDefaultPage(new_id)

        
    if shasattr(self, '_lp_outdated'):
        delattr(self, '_lp_outdated')
        
I18NBaseObject.processForm = processForm
