KEEP = [
'/about',
'/good_practice',
'/legislation',
'/topics',
'/priority_groups',
'/statistics',
'/publications',
'/press_room'
'/sector',
'/campaigns'
]

def cleanup(self):
  pc = self.portal_catalog
  res = pc(portal_type="I18NFolder")
  ppath = self.portal_url.getPortalPath()
  cnt = 0
  for r in res:
    print r.getPath().replace(ppath, '')
    if r.getPath().replace(ppath, '') in KEEP: 
      continue
    ob = r.getObject()
    ob.setExcludeFromNav(True)
    ob.reindexObject()
    cnt = cnt +1
  return "%s objects excluded" % cnt
