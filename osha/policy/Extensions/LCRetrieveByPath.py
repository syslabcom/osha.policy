import transaction
from zLOG import LOG, INFO

def retrieve(self):
  pc = self.portal_catalog
  link_checker = self.portal_linkchecker
  ST = []
  path = self.REQUEST.get('path', '/'.join(self.getPhysicalPath()))
  langs = self.REQUEST.get('langs',
          self.portal_languages.getSupportedLanguages())
  if "%s" in path:
      paths = [path%lang for lang in langs]
  else:
      paths = [path]

  LOG("LCRetrieveByPath", INFO, "Starting retrieval")
  LOG("LCRetrieveByPath", INFO, "Paths: %s" % str(paths))
  LOG("LCRetrieveByPath", INFO, "Langs: %s" % str(langs))

  for path in paths:
    LOG("LCRetrieveByPath", INFO, "> Path %s"%path)
    results = pc(Language=langs,  path=path)
    LOG("LCRetrieveByPath", INFO, "> %s results found"%len(results))
    cnt = 0
    for result in results:
      try:
        object = result.getObject()
      except:
        continue
      if not object: continue
      link_checker.retrieving.retrieveObject(object)
      LOG("LCRetrieveByPath", INFO, "> Retrieved %s"%result.getPath())
      ST.append("retrieved %s" % result.getPath())
      cnt += 1
      if cnt%10==0:
        transaction.commit()
        LOG("LCRetrieveByPath", INFO, "Committing %s of %s" %(cnt, len(results)))

  LOG("LCRetrieveByPath", INFO, "Fertig")
  return "\n".join(ST)


