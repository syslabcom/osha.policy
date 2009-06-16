from Acquisition import aq_parent
from zLOG import WARNING
from zLOG import LOG as zLOG
from Products.Archetypes.event import ObjectInitializedEvent
from zope.app.container.contained import ContainerModifiedEvent

ident = 'osha.policy'

def handle_object_willbe_translated(event):
    object = event.object
    object = object.getCanonical()
    language = event.language
    myLL = None
    llinks =  object.getBRefs('lingualink')
    for llink in llinks:
        if llink.Language() == language:
            myLL = llink
            break
    if myLL:
        try:
            aq_parent(myLL).manage_delObjects(myLL.getId())
        except Exception, err:
            text = "Unable to delete LinguaLink in language '%s' on object %s prior to adding translation" %(
                language, object.absolute_url())
            zLOG(ident, WARNING, text, error=str(err))


# If a canonical object gets saved, reindex all translations to keep the catalog
# up to date for the language-independent fields.
# Only proceed on user request (indicated by ticking a checkbox)
def handle_objectModified(object, event):
    if isinstance(event, ObjectInitializedEvent) or isinstance(event, ContainerModifiedEvent):
        return
    try:
        isCanonical = object.isCanonical()
    except Exception, err:
        return
    if not isCanonical:
        return
    if 'portal_factory' in object.getPhysicalPath():
        return

    # only proceed if the user has checked the appropriate box
    # and the object has that field in its schema
    field = object.getField('reindexTranslations')
    if object.REQUEST.get('reindexTranslations', False) and field:
        trans = object.getTranslations()
        del trans[object.Language()]
        for transObject, state in trans.values():
            transObject.reindexObject()

        # reset the field to False
        field.getMutator(object)(False)
