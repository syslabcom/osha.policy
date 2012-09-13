from gocept.linkchecker.retrievemanager import RetrieveManager
from AccessControl import getSecurityManager
from zope.component import getUtility
from plone.app.async.interfaces import IAsyncService
from gocept.linkchecker.interfaces import IRetriever
from Products.Archetypes.interfaces import IReferenceable

# CMF/Plone imports
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger('osha.policy.retieve')


def job_failure_callback(result):
    logger.error(result)


def retrieve_async(context, path, online):
    obj = context.restrictedTraverse(path)
    lc = getToolByName(obj, 'portal_linkchecker')
    database = lc.database
    database.unregisterObject(obj)
    retriever = IRetriever(obj, None)
    if retriever is not None:
        links = retriever.retrieveLinks()
        database.registerLinks(links, obj, online)


def retrieveObject(self, object, online=False):
    # Check for ModifyPortalContent-Permission on context object.
    # This is dangerous, but I think I know what I'm doing.
    sm = getSecurityManager()
    if not sm.checkPermission(ModifyPortalContent, object):
        return
    if (not IReferenceable.providedBy(object)):
        return
    retriever = IRetriever(object, None)
    if retriever is not None:
        async = getUtility(IAsyncService)
        tpath = '/'.join(object.getPhysicalPath())
        job = async.queueJob(retrieve_async, object, tpath, online)
        callback = job.addCallbacks(failure=job_failure_callback)

RetrieveManager.retrieveObject = retrieveObject
