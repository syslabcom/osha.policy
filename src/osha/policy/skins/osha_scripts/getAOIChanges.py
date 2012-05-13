## Script (Python) "getAOIChanges"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=period=60
##title=gets the changes in a given Area Of Interest (AOI), the aoi keyword
## is given in the path as next element
##
# fetch the id of the AOI which is given in the path like this: /.../aoi_fetch_changes/accident_prevention
path = context.REQUEST.get('PATH_INFO', '')
elems = path.split('/')
meidx = elems.index('aoi_fetch_changes')
if len(elems)>meidx+1:
  aoi = elems[meidx+1]
  if '?' in aoi:
    aoi = aoi.split('?')[0]

id = aoi


from Products.PythonScripts.standard import html_quote
request = container.REQUEST
RESPONSE =  request.RESPONSE

from DateTime import DateTime
from Products.AdvancedQuery import Eq, Ge, In, Or, And
CAT = context.portal_catalog
if hasattr(CAT, 'getZCatalog'):
  CAT = CAT.getZCatalog()


topiclist = context.GLOBALSETTINGS.TopicsOfInterest()
for TOP in topiclist:
  if TOP['id'] == id:
    break
MTSubjectPath = TOP.get('MTSubjectPath', '')
osha_keywords = TOP.get('osha_keywords', '')
path = TOP.get('path', '')

today = DateTime().earliestTime()
delta= (today-period).Date()

query = And( Ge('modified', delta), Eq('review_state', 'published') )
if MTSubjectPath!='' and osha_keywords!='':
  query = query & Or(Eq('osha_keywords', osha_keywords), In('MTSubjectPath', MTSubjectPath) )
if path:
  query = query & Eq('path', path)

sortSpec = (('modified', 'desc'),)


RESMAP = {}
res = CAT.evalAdvancedQuery(query, sortSpec)

for R in res:
  T = R.portal_type
  list = RESMAP.get(T, [])
  list.append(R)
  RESMAP[T] = list


numresults = len(res)
#if numresults>30:
#  res = res[:30]
return context.aoi_template(results=RESMAP, notification_period=period, user_name='admin', numresults=numresults, modification_date=delta, siteurl="http://osha.europa.eu")
