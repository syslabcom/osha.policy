from DateTime import DateTime

def update(self):
  start = DateTime()
  db = self.portal_linkchecker.aq_inner.database
  db._updateWSRegistrations()
  stop = DateTime()
  delta = (stop-start)*84600
  return "update took %s seconds" % delta

