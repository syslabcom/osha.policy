import transaction
from zLOG import LOG, INFO, BLATHER
from plone.app.async.interfaces import IAsyncService
from zope.component import getUtility
from Products.Archetypes.interfaces import IReferenceable
from AccessControl import getSecurityManager
from Products.CMFCore.permissions import ModifyPortalContent
from osha.policy.handlers import job_failure_callback, retrieve_async, unregister_async
from slc.outdated import ANNOTATION_KEY
from zope.annotation.interfaces import IAnnotatable, IAnnotations

# This script can be run on a given path. if the keyword resume is given, it will not retrive again but only resume current paths

def retrieve(self):
  ST = []
  pc = self.portal_catalog
  link_checker = self.portal_linkchecker
  async = getUtility(IAsyncService)
  sm = getSecurityManager()
  # INitialize the helperattribute to store paths to retrieve
  objpaths = getattr(link_checker, 'objpaths', None)
  cleanup = self.REQUEST.get('cleanup', False)

  if objpaths is None or cleanup=='1':
    link_checker.objpaths = []
    objpaths = []

  # Check wheter we start fresh or need to resume
  resume = self.REQUEST.get('resume')
  debug = self.REQUEST.get('debug')
  LOG("LCRetrieveByPath", INFO, "Resuming retrieval with %s paths" % len(objpaths))

  if len(objpaths)==0 and not resume:
    path = self.REQUEST.get('path', '/'.join(self.getPhysicalPath()))
    alllangs = self.portal_languages.getSupportedLanguages()
    langs = self.REQUEST.get('langs', alllangs)
    print "path: %s" %path
    if "%s" in path:
      paths = [path%lang for lang in langs]
    else:
      paths = [path]

    LOG("LCRetrieveByPath", INFO, "Starting retrieval")

    for path in paths:
      LOG("LCRetrieveByPath", INFO, "> Path %s"%path)
      results = pc(Language='all',  path=path)
      objpaths = [x.getPath() for x in results]
      link_checker.objpaths += objpaths
      LOG("LCRetrieveByPath", INFO, "> %s results found"%len(results))

  # DONE Retrieving objpaths, start checkretrieval

  cnt = 0
  objpaths = [x for x in link_checker.objpaths]
  total = len(objpaths)
  for path in objpaths:
      if debug:
          print path
      try:
          ob = self.unrestrictedTraverse(path)
      except:
          continue
      if not ob:
          continue
      if not sm.checkPermission(ModifyPortalContent, ob):
          continue 
      if (not IReferenceable.providedBy(ob)):
          continue
      outdated = IAnnotatable.providedBy(ob) and \
          IAnnotations(ob).get(ANNOTATION_KEY, False) or False
      if outdated:
          LOG("CMFLinkChecker", INFO, "unregistering %s, object is outdated" % path)
          links = link_checker.database.getLinksForObject(ob)
          link_ids = [x.getId() for x in links]
          job = async.queueJob(unregister_async, link_checker, link_ids)
          callback = job.addCallbacks(failure=job_failure_callback)
          continue
      job = async.queueJob(retrieve_async, ob, path, online=False)
      callback = job.addCallbacks(failure=job_failure_callback)
      LOG("LCRetrieveByPath", INFO, "> Retrieved %s"%path)
      ST.append("retrieved %s" % path)
      link_checker.objpaths.remove(path)
      link_checker._p_changed = 1
      cnt += 1
      if cnt%10==0:
          transaction.commit()
          LOG("LCRetrieveByPath", INFO, "Committing %s of %s" %(cnt, total))

  LOG("LCRetrieveByPath", INFO, "Fertig")
  return "\n".join(ST)


