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
import csv
import codecs
from StringIO import StringIO

filename = "/tmp/extraction-info.csv"

IGNORE = []
MAXDEPTH = 0
HEADER = ['path', 'language', 'country', 'creation date', 'modification date',
    'title', 'description', 'category', 'nace', 'thesaurus', 'type', 'size',
    'creator', 'remote language', 'review state', 'start date', 'end date']
DEBUG = 0

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
        if DEBUG:
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

def get_unicode_text(text):
    if isinstance(text, unicode):
        return text
    for encoding in ['utf-8', 'utf-16', 'cp1252', 'latin-1', 'iso8859-1']:
        try:
            return unicode(text, encoding)
        except UnicodeDecodeError:
            pass
    return ""


def export(self):
    response = self.REQUEST and self.REQUEST.RESPONSE or None
    maxdepth = self.REQUEST.get('maxdepth', MAXDEPTH)
    try:
        maxdepth = int(maxdepth)
    except:
        maxdepth = MAXDEPTH
    only_en = bool(self.REQUEST.get('onlyen', False))
    include_data = bool(self.REQUEST.get('include_data_folder', False))
    log = setupLog(self, response)
    start_time = DateTime()
    log.write('<h2>Contents metadata export</h2>')
    log.write('Starting at ' + `start_time.ISO()`)
    log.write('Maximum depth (set using maxdepth= in the URL): <strong>%d</strong>' % maxdepth)
    log.write('English only (set using onlyen=1 in the URL)? <strong>%s</strong>' % only_en)
    log.write('Include /data folder (set using include_data_folder=1 in the URL)? <strong>%s</strong>' % include_data)
    doRecurse = True
    
    pwt = getToolByName(self, 'portal_workflow')

    dialect = csv.excel()
    # we use semicolon instead of comma, seems to be Excel standard now
    dialect.delimiter = ';'
    dialect.quoting = csv.QUOTE_ALL
    
    fh = open(filename, 'w')
    fh.write(codecs.BOM_UTF8)
    writer = csv.writer(fh, dialect=dialect)
    writer.writerow(HEADER)
    
    statistics = dict()

    def do(item, doRecurse=True, level=0):
        if item.id in IGNORE:
            return
        # Only first XX levels:
        if maxdepth>-1 and level>maxdepth:
            doRecurse=False
        log.write("* Export item %s" % '/'.join(item.getPhysicalPath()))
        line = list()
        line.append('/'.join(item.getPhysicalPath()))
        line.append(hasattr(item.aq_explicit, 'Language') and item.Language() or '')
        country = hasattr(item.aq_explicit, 'getCountry') and item.getCountry() or ''
        if country:
            country = ','.join(country)
        line.append(country)
        line.append(hasattr(item.aq_explicit, 'created') and item.created().strftime('%Y-%m-%d') or 'n/a')
        line.append(hasattr(item.aq_explicit, 'modified') and item.modified().strftime('%Y-%m-%d') or 'n/a')
        title = item.title_or_id()
        line.append(get_unicode_text(title))
        description = hasattr(item.aq_explicit, 'Description') and item.Description() or ''
        # This sad hack is necessary to appease M$-Excel
        # Of course, LibreOffice and iWorks Numbers know what's an EOL and
        # whats not...
        description = description.replace('\r\n', ' ').replace('\n', ' ')
        line.append(get_unicode_text(description))
        line.append(hasattr(item.aq_explicit, 'Subject') and ','.join(item.Subject()) or '')
        line.append(hasattr(item.aq_explicit, 'getNace') and \
            ','.join(item.getNace()) or "")
        line.append(hasattr(item.aq_explicit, 'getMultilingual_thesaurus') and \
            ','.join(item.getMultilingual_thesaurus()) or "")
        line.append(hasattr(item.aq_explicit, 'portal_type') and item.portal_type or item.meta_type)
        sizer = item.restrictedTraverse('getObjSize', None)
        try:
            size = sizer and sizer() or '0 kB'
        except: # No blob file
            size = '0 kB'
        line.append(size)
        line.append(hasattr(item.aq_explicit, 'Creator') and item.Creator() or '')
        line.append(hasattr(item.aq_explicit, 'getRemoteLanguage') and \
            ','.join(item.getRemoteLanguage()) or '')
        try:
            wf_state = pwt.getInfoFor(item, 'review_state')
        except:
            wf_state = ''
        line.append(wf_state)
        start_date = hasattr(item.aq_explicit, 'start') and item.start()
        line.append(start_date and start_date.strftime('%Y-%m-%d') or '')
        end_date = hasattr(item.aq_explicit, 'end') and item.end()
        line.append(end_date and end_date.strftime('%Y-%m-%d') or '')

        writer.writerow([x and x.encode("UTF-8") or '' for x in line])

        if doRecurse and hasattr(item.aq_explicit, 'objectValues'):
            log.write('Contents of sub-folder %s' % '/'.join(item.getPhysicalPath()))
            for id in item.objectIds():
                try:
                    ob = getattr(item, id)
                except:
                    ob = None
                if ob:
                    do(ob, doRecurse, level+1)
            

    portal = getToolByName(self, 'portal_url').getPortalObject()
    langs = getToolByName(self, 'portal_languages').getSupportedLanguages()
    langs.sort()
    if only_en:
        langs = ['en']
    else:
        langs = ['en'] + [x for x in langs if x != 'en']
    if include_data:
        langs.append('data')

    for lang in langs:
        start = getattr(portal, lang, None)
        if start is None:
            print "No top-level folder for language %s" % lang
            continue
        log.write('<h3>Handling top-level folder "%s"</h3>' % lang)
        do(start, True, 0)

    fh.close()
    finished = DateTime()
    delta = (finished-start_time)
    log.write('<br/><br/>Finished at ' + `finished.ISO()`)

    finish(self, response)

