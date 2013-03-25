from AccessControl import getSecurityManager
from Acquisition import aq_parent
from DateTime import DateTime
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.interfaces import IReferenceable
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.FactoryTool import TempFolder
from gocept.linkchecker.interfaces import IRetriever
from plone.app.async.interfaces import IAsyncService
from utils import extractPDFText
from zope.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.container.contained import ContainerModifiedEvent
from zope.component import getUtility

import gocept.linkchecker.link
import gocept.linkchecker.url
import logging
import pyPdf
import zope.component

log = logging.getLogger('osha.policy/handlers.py')


def job_failure_callback(result):
    log.error(result)


def handle_auto_translated_files(event):
    """ Set the title, if retrieved from the pdf file.
    """
    file = event.object
    parent = event.object.aq_parent

    data_folder_id = '%s_data' % file.getFile().filename.rsplit('.')[0]
    if hasattr(parent, data_folder_id):
        parent.manage_delObjects(ids=[data_folder_id])

    file_obj = file.getFile()
    if hasattr(file_obj, 'getBlob'):
        file_obj = file_obj.getBlob()

    if hasattr(file_obj, 'open'):
        f = file_obj.open()
    else:
        # Don't yet know why, but this happens during doctests
        return

    reader = pyPdf.PdfFileReader(f)
    docinfo = reader.getDocumentInfo()
    for attr, field in [
        ('title', 'title'),
        ('subject', 'description'),
        ('creator', 'creators'),
    ]:
        val = docinfo.get(attr)
        if val is not None:
            file.Schema().get(field).set(file_obj, val)

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
    llinks = object.getBRefs('lingualink')
    for llink in llinks:
        if llink.Language() == language:
            myLL = llink
            break
    if myLL:
        try:
            aq_parent(myLL).manage_delObjects(myLL.getId())
        except Exception, err:
            text = "Unable to delete LinguaLink in language "\
                "'%s' on object %s prior to adding translation" % (
                language, object.absolute_url())
            log.warn('%s %s' % (str(err), text))


# If a canonical object gets saved, reindex all translations to keep the
# catalog up to date for the language-independent fields.
# Only proceed on user request (indicated by ticking a checkbox)
def handle_objectModified(object, event):
    if isinstance(event, ObjectInitializedEvent) or \
            isinstance(event, ContainerModifiedEvent):
        return
    try:
        isCanonical = object.isCanonical()
    except Exception:
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


def unregister_async(lc, link_ids):
    log.info('unregister_async')
    database = lc.database
    database.manage_delObjects(link_ids)


@zope.component.adapter(
    zope.app.container.interfaces.IObjectRemovedEvent)
def remove_links(event):
    object = event.object
    try:
        link_checker = getToolByName(object, 'portal_linkchecker').aq_inner
        db = link_checker.database
    except AttributeError:
        return
    if isinstance(object, (gocept.linkchecker.url.URL,
                           gocept.linkchecker.link.Link)):
        return
    links = db.getLinksForObject(object)
    link_ids = [x.getId() for x in links]
    async = getUtility(IAsyncService)
    job = async.queueJob(unregister_async, link_checker, link_ids)
    callback = job.addCallbacks(failure=job_failure_callback)
    callback  # for pep


def retrieve_async(context, path, online):
    log.info('retrieve_async')
    obj = context.restrictedTraverse(path)
    lc = getToolByName(obj, 'portal_linkchecker')
    database = lc.database
    database.unregisterObject(obj)
    retriever = IRetriever(obj, None)
    if retriever is not None:
        links = retriever.retrieveLinks()
        database.registerLinks(links, obj, online)


def is_publically_visible(obj):
    """Anonymous has the View permission"""
    roles = obj.rolesOfPermission("View")
    role_names = [i["name"] for i in roles if i['selected'] == 'SELECTED']
    return "Anonymous" in role_names


def is_outdated(obj):
    if IAnnotatable.providedBy(obj):
        return IAnnotations(obj).get('slc.outdated', False)


@zope.component.adapter(
    zope.lifecycleevent.interfaces.IObjectModifiedEvent)
def update_links(event):
    obj = event.object
    if is_outdated(obj) or not is_publically_visible(obj):
        return
    temporary = hasattr(obj, 'meta_type') and \
        obj.meta_type == TempFolder.meta_type
    if temporary:
        # Objects that are temporary (read: portal_factory) and do not have a
        # (stable) URL (yet) do not need to be crawled: relative links will be
        # off quickly and we can't really use the UID anyway.
        return
    try:
        link_checker = getToolByName(obj, 'portal_linkchecker').aq_inner
    except AttributeError:
        return
    if not link_checker.active:
        return
    retriever = IRetriever(obj, None)
    if retriever is not None:
        sm = getSecurityManager()
        if not sm.checkPermission(ModifyPortalContent, obj):
            return
        if (not IReferenceable.providedBy(obj)):
            return
        async = getUtility(IAsyncService)
        tpath = '/'.join(obj.getPhysicalPath())
        job = async.queueJob(retrieve_async, obj, tpath, online=True)
        callback = job.addCallbacks(failure=job_failure_callback)
        callback  # for pep


def handle_edit_begun(obj, event):
    """ If an object gets edited and has no effective date yet,
        its effective date will be set to the current date.
    """
    if not obj.getEffectiveDate():
        now = DateTime().strftime('%Y-%m-%d')
        obj.setEffectiveDate(now)


def updateManyStates_async(context, update_list):
    """ We do that async because it writes status to the objects in
        portal_linkchecker.database. This takes time. If it takes
        longer, haproxy might close the connection
    """
    log.info('updateManyStates_async')
    lc = context.restrictedTraverse('portal_linkchecker')
    database = lc.database
    for url, state, reason in update_list:
        database.updateLinkStatus(url, state, reason)


def updateManyStates(self, client_id, password, update_list):
    """XML-RPC connector for LMS"""
    self.authenticateXMLRPC(client_id, password)
    portal = self.portal_url.getPortalObject()
    async = getUtility(IAsyncService)
    job = async.queueJob(updateManyStates_async, portal, update_list)
    callback = job.addCallbacks(failure=job_failure_callback)
    callback  # for pep


def handle_outdated_links(obj, event):
    """When an item is marked as outdated, remove the links from the
    link checker, when it is unmarked as outdated add them again.
    """
    is_outdated = event.status
    if is_outdated:
        remove_links(event)
    else:
        update_links(event)


def handle_public_links(obj, event):
    """Only check links for publically visible items, remove links in
    unpublished items from the link checker database.
    """
    publically_visible = is_publically_visible(obj)
    if publically_visible:
        update_links(event)
    else:
        remove_links(event)
