"""
Data to export:
- path
- language
- country (if given)
- creation date
- modification date
- title
- description (if given)
- category (if given)
- nace (if given)
- thesaurus (if given)
- type (page, news, event, publication etc)
- size
- Creator
- remote language (if given)
- folder or document?
- review state (published or private etc)
- start and end date for events

"""


import logging
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

filename = "/Users/thomas/tmp/extraction-info.csv"
IGNORE = []

logger = logging.getLogger('osha.policy.ExtractContentInformation')

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


def export(self):
    response = self.REQUEST and self.REQUEST.RESPONSE or None
    log = setupLog(self, response)
    start_time = DateTime()
    log.write('<h2>Contents metadata export</h2>')
    log.write('Starting at ' + `start_time.ISO()`)
    doRecurse = True
    
    pwt = getToolByName(self, 'portal_workflow')

    fh = open(filename, 'w')

    def do(item, doRecurse=True, level=0):
        if item.id in IGNORE:
            return
        # Only first XX levels:
        if level>0:
            doRecurse=False
        log.write("Do something for item %s" % '/'.join(item.getPhysicalPath()))
        line = list()
        line.append('/'.join(item.getPhysicalPath()))
        line.append(hasattr(item.aq_explicit, 'Language') and item.Language() or '')
        line.append(hasattr(item.aq_explicit, 'getCountry') and \
            ','.join(item.getCountry()) or "no country")
        line.append(hasattr(item.aq_explicit, 'created') and item.created().ISO() or 'n/a')
        line.append(hasattr(item.aq_explicit, 'modified') and item.modified().ISO() or 'n/a')
        title = item.title_or_id()
        try:
            title = title.decode('utf-8')
        except:
            # despair?
            pass
        line.append(title)
        description = hasattr(item.aq_explicit, 'Description') and item.Description() or ''
        try:
            description = description.decode('utf-8')
        except:
            pass
        line.append('"%s"' % description)
        line.append(hasattr(item.aq_explicit, 'Subject') and ','.join(item.Subject()) or '')
        line.append(hasattr(item.aq_explicit, 'getNace') and \
            ','.join(item.getNace()) or "no NACE")
        line.append(hasattr(item.aq_explicit, 'getMultilingual_thesaurus') and \
            ','.join(item.getMultilingual_thesaurus()) or "no thesaurus")
        line.append(hasattr(item.aq_explicit, 'portal_type') and item.portal_type or item.meta_type)
        sizer = item.restrictedTraverse('getObjSize', None)
        line.append(sizer and sizer() or '0 kB')
        line.append(hasattr(item.aq_explicit, 'Creator') and item.Creator() or '')
        line.append(hasattr(item.aq_explicit, 'getRemoteLanguage') and \
            ','.join(item.getRemoteLanguage()) or '')
        try:
            wf_state = pwt.getInfoFor(item, 'review_state')
        except:
            wf_state = ''
        line.append(wf_state)
        line.append(hasattr(item.aq_explicit, 'start') and item.start().ISO() or '')
        line.append(hasattr(item.aq_explicit, 'end') and item.end().ISO() or '')

        out = u";".join(line) #.decode('utf-8')
        fh.write(out.encode('utf-8'))
        fh.write("\n")

        if doRecurse and hasattr(item.aq_explicit, 'objectValues'):
            print len(item.objectValues())
            for ob in item.objectValues():
                do(ob, doRecurse, level+1)

    portal = getToolByName(self, 'portal_url').getPortalObject()
    langs = getToolByName(self, 'portal_languages').getSupportedLanguages()
    langs.sort()
    langs = ['en'] + [x for x in langs if x != 'en']

    for lang in langs[:3]:
        start = getattr(portal, lang, None)
        if start is None:
            print "No top-level folder for language %s" % lang
            continue
        log.write('<h3>Handling language "%s"</h3>' % lang)
        do(start, doRecurse, 0)

    fh.close()
    finished = DateTime()
    delta = (finished-start_time)
    log.write('<br/><br/>Finished at ' + `finished.ISO()`)


    finish(self, response)
