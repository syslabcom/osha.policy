def lcregisterThis(self):
  lc = self.portal_linkchecker.aq_inner
  lc.retrieveObject(self)
  return "retrieved"
