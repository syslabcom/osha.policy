def helper(self):
  print "\nhelper"

  folderid="press"
  pageid="front-page"

  portal = self.portal_url.getPortalObject()
  langs = portal.portal_languages.getSupportedLanguages()

  for lang in langs:
    base=getattr(portal, lang, None)
    if not base: print "ERR no folder for ", lang;continue
    try:
      folder = getattr(base, folderid, None)
      folder._setProperty('default_page', pageid, 'string')
      print "ok for ", [folder]
    except Exception,e:
      print "Err for lang:", lang, str(e)


  return "ok"
