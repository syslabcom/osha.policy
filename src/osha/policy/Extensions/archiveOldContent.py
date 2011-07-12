import logging
import transaction
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getSiteEncoding
from Products.statusmessages.interfaces import IStatusMessage
from slc.linguatools.utils import toggle_outdated

allowed_types = ['News Item', 'Event', 'PressRelease']

logger = logging.getLogger('osha.policy.archiveOldContent')

br = '<br />'
link = '<a href="%(url)s">%(text)s</a>' + br

class LogWriter(object):

    def __init__(self, response=None):
        self.response = response

    def write(self, msg):
        if self.response:
            if isinstance(msg, unicode):
                msg = msg.encode(getSiteEncoding(self))
            self.response.write(msg + br)
        logger.info(msg)

    def close(self):
        self.log.close()


def setupLog(self, response):
    log = LogWriter(response)
    if response:
        response.setHeader('Content-Type', 'text/html;charset=UTF-8')
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Pragma', 'no-cache')
        self.backlink = link % dict(url=self.absolute_url() + '/manage_workspace',
                               text='Back to ZMI')
        response.write('<html><body>')
        response.write(self.backlink)
        response.write(br)
    return log

def finish(self, response):
    if response:
        response.write(br)
        response.write(self.backlink)



def archiveByType(self, portal_type=None, age_in_days=None, limit=0):
    response = self.REQUEST and self.REQUEST.RESPONSE or None
    log = setupLog(self, response)
    if not portal_type:
        return "You need to specify portal_type"
    if portal_type not in allowed_types:
        return "Only the following portal types are allowed: %s" %\
            ', '.join(allowed_types)
    if not age_in_days:
        return "You must provide age_in_days to indicate up to which day " \
            "content should become outdated. Example: age_in_days=180 for " \
            "6 months and older."
    try:
        days = int(age_in_days)
    except:
        return "The value passed for age_in_days is not a valid integer"
    try:
        limit = int(limit)
    except:
        return "The value passed for limit is not a valid integer"
    log.write('<h2>Bulk-outdate content</h2>')
    log.write('Starting at ' + `DateTime().ISO()`)
    log.write('<h3>Settings</h3><p>portal_type: %s, age_in_days: %d, limit: %d</p>' % (
        portal_type, days, limit))
    pc = getToolByName(self, 'portal_catalog')
    now = DateTime()
    date = now - days
    # hardcoded to corporate site
    query = dict(portal_type=portal_type,
        path="/osha/portal/en",
        Language='all',
        modified=dict(query=date, range='max'))
    res = pc(query)
    logger.info("I have %d results" % len(res))
    trans_count = 0
    count = 0
    if limit > 0:
        res = res[:limit]
    for r in res:
        try:
            obj = r.getObject()
        except:
            logger.warn("Error getting object for %s" % r.getPath())
            continue
        for lang in obj.getTranslations():
            trans = obj.getTranslation(lang)
            url = trans.absolute_url()
            logger.info('Handling item %s' % url)
            view = trans.restrictedTraverse('@@object_toggle_outdated')
            msg = view.toggle(True)
            msg += u" (<a href='%(url)s'>%(url)s</a>)" % dict(url=url)
            log.write(msg)
            trans_count += 1
        count += 1
        if count % 10 == 0:
            transaction.commit()
            log.write("<br /><strong>Committing after %s items</strong><br />" % count)

    log.write('<br/><br/>Finished at ' + `DateTime().ISO()`)
    log.write('A total of %d objects (including translations) were modified.' % trans_count)
    finish(self, response)

