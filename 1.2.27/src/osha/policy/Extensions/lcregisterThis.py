def lcregisterThis(self):
  lc = self.portal_linkchecker.aq_inner
  lc.retrieving.retrieveObject(self)
  return "retrieved"
