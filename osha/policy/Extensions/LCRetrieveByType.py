import transaction

def retrieve(self):
  pc = self.portal_catalog
  link_checker = self.portal_linkchecker
  ST = []
  portal_type='Provider'
  results = pc(Language='all', portal_type=portal_type)
  cnt = 0
  for result in results:
    object = result.getObject()
    link_checker.retrieving.retrieveObject(object)
    ST.append("retrieved %s" % object.getId())
    cnt += 1
    if cnt%10==0:
      transaction.savepoint()

  return "\n".join(ST)


