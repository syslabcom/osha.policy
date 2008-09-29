import transaction
from zLOG import LOG, INFO

def retrieve(self):
  pc = self.portal_catalog
  link_checker = self.portal_linkchecker
  ST = []
  langs = self.portal_languages.getSupportedLanguages()
  langs = ['sl', 'sk', 'sv']
  lpath = "/osha/portal/%s/campaigns"
  LOG("LCRetrieveByType", INFO, "Starting retrieval")
  #path = "/osha/portal/data"
  #langs=["en"]
  for lang in langs:
    LOG("LCRetrieveByType", INFO, "> Language %s"%lang)
    #results = pc(Language='all',  path=path)
    results = pc(Language='all',  path=lpath%lang)
    #results = pc(Language='all', portal_type=portal_type, path=lpath%lang)
    LOG("LCRetrieveByType", INFO, "> %s results found"%len(results))
    cnt = 0
    for result in results:
      try:
        object = result.getObject()
      except:
        continue
      if not object: continue
      link_checker.retrieving.retrieveObject(object)
      LOG("LCRetrieveByType", INFO, "> Retrieved %s"%result.getPath())
      ST.append("retrieved %s" % result.getPath())
      cnt += 1
      if cnt%10==0:
        transaction.commit()
        LOG("LCRetrieveByType", INFO, "Committing %s of %s" %(cnt, len(results)))
        #transaction.savepoint()

  LOG("LCRetrieveByType", INFO, "Fertig")
  return "\n".join(ST)


