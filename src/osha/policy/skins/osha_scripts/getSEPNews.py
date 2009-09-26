## Script (Python) "getSEPNews"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=topic=''
##title=returns news in a listing for a Single Entry Point (SEP)
##
from Products.AdvancedQuery import In, Eq, Le, Ge, And, Or
from DateTime import DateTime

pc = context.portal_catalog
if hasattr(pc, 'getZCatalog'):
  pc = pc.getZCatalog()

now = DateTime()

query = Eq('portal_type', 'News Article')   & Ge('expires', now, filter=True)  & Eq('review_state', 'published')
#& Eq('osha_keywords', topic)
res = pc.evalAdvancedQuery(query, (('effective', 'desc'),) )

return res[:min(len(res), 5)]

