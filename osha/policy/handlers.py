import logging
import pyPdf
from Acquisition import aq_parent
from zope.app.container.contained import ContainerModifiedEvent
from plone.app.blob.interfaces import IBlobWrapper
from Products.Archetypes.event import ObjectInitializedEvent

from utils import extractPDFText

log = logging.getLogger('osha.policy/handlers.py')

def handle_auto_translated_files(event):
    """ Set the title, if retrieved from the pdf file.
    """
    file = event.object
    parent = event.object.aq_parent 

    data_folder_id = '%s_data' % file.getFile().filename.rsplit('.')[0]
    if hasattr(parent, data_folder_id):
        parent.manage_delObjects(ids=[data_folder_id])

    file_obj = file.getFile().getBlob()
    f = file_obj.open()
    reader = pyPdf.PdfFileReader(f)
    docinfo = reader.getDocumentInfo()
    for attr, field in [
                ('title', 'title'), 
                ('subject', 'description'), 
                ('creator', 'creators'), 
                ]:
        val = docinfo.get(attr) 
        if val is not None:
            file.Schema().get(field).set(trans_file, val)

    if docinfo.title is None:
        # Attempt to extract the title from the pdf text
        page = reader.getPage(0)
        text = extractPDFText(page)
        content = text.replace(u"\xa0", " ").strip().split('\n')
        # Complete thumbsuck...
        title = content[2]
        file.setTitle(title)
    f.close()


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
            log.warn('%s %s' % (str(err), text))


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
