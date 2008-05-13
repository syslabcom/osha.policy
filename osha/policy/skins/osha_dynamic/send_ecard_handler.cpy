## Script (Python) "send_ecard_handler"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = container.REQUEST
import random

from osha.policy.utils import logit

pw = context.portal_workflow
portal = context.portal_url.getPortalObject()
ecard_id = request.get('ecard_id')
#ecardtext = request.get('ecardtext')
ecardrecipients = request.get('ecardrecipients')
youremail = request.get('youremail')
yourname = request.get('yourname')
ecard = getattr(portal.images, ecard_id)
ecard_url = ecard.absolute_url


r = int(random.random()*10000000000)
dt = DateTime().strftime('%Y%m%d%H%M%S')
cid = "%s-%s" %(dt,r)
cardpath = "%s/display_ecard?id=%s" %(portal.absolute_url(), cid)


usertitle = "View the eCard sent to you by %s" % yourname
conftitle = "Here's a copy of your card"

portal.sql.ecard_sql_insert(ecard_key=cid, sender_name=yourname, ecard_name=ecard_id)

# limit to 20
for ecardrecipient in ecardrecipients[:20]:
    useremail = context.ecard_email_template(cardpath=cardpath, ecardrecipient=ecardrecipient, youremail=youremail, usertitle=usertitle)
    context.MailHost.secureSend(useremail, mto=ecardrecipient, mfrom=youremail, subject=usertitle, charset="utf-8")

confemail = context.ecard_email_template(cardpath=cardpath, ecardrecipient=ecardrecipient, youremail=youremail, usertitle=usertitle)
context.MailHost.secureSend(useremail, mto=youremail, mfrom='ecards@osha.europa.eu', subject=conftitle)


state.set(status='success', context=context)
return state

