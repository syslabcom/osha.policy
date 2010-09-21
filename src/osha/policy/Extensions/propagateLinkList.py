from slc.linkcollection.interfaces import ILinkList

def locurls(lang, urls):
  lurls = []
  for url in urls:
    lurl = url.replace('/en/', '/%s/' % lang)
    lurls.append(lurl)
  return lurls

def propagateLinkList(self):
  LL = ILinkList(self)
  langs = self.getTranslations()
  urls = LL.urls

  for lang in langs.keys():
    trans = langs[lang][0]
    ILinkList(trans).urls = locurls(lang, urls)
  
  return "ok"
