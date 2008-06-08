from Acquisition import aq_parent
from zLOG import WARNING
from zLOG import LOG as zLOG

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
