 # -*- coding: utf-8 -*-

# from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import isExpired, safe_unicode
from Products.Five.browser import BrowserView
from StringIO import StringIO
# from plone.app.async.interfaces import IAsyncService
# from zope.component import getUtility
# from slc.linguatools import utils
# from slc.outdated.adapter import ANNOTATION_KEY
# from zope.annotation.interfaces import IAnnotatable, IAnnotations
from osha.theme.browser.utils import search_solr
from ordereddict import OrderedDict
# from zope.component import queryUtility

import csv
import logging
log = logging.getLogger('osha.policy.export')


csv.register_dialect(
    'bilbomatica', delimiter=';', doublequote=False, escapechar='\\',
    quoting=csv.QUOTE_ALL,
)


def handleString(value):
    value = safe_unicode(value).strip()
    return value.encode('utf-8')

def handleBool(value):
    if value:
        return "1"
    return "0"

def handleText(value):
    value = safe_unicode(value).strip()
    value = value.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    return value.encode('utf-8')

def handleList(value):
    return ", ".join([
        "'{0}'".format(safe_unicode(x).encode('utf-8')) for x in value])

def handleDate(value):
    return value.strftime('%Y-%m-%d %H:%M:%S')


class BaseExporter(BrowserView):
    """Exports content into csv """

    query = ''
    limit = 10
    search_parameters = {}
    metadata_fields = [
        'path', 'language', 'workflow_state', 'creation_date', 'modification_date', 'creator'
    ]
    fields = []
    name = 'generic'

    def __call__(self):
        response = self.request.RESPONSE
        self.set_response_headers(response)
        return self.export_data()

    def set_up_parameters(self, context):
        """ Provide hook for intial setup,
        extend in the content-type based classes """
        self.paths = [
            '/osha/portal/{0}'.format(lang) for lang in self.languages]
        self.search_parameters['rows'] = self.limit
        self.search_parameters['start'] = 0

    def skip_result(self, brain, obj):
        return False

    def export_data(self):
        context = self.context
        self.pwt = getToolByName(context, 'portal_workflow')
        self.plt = getToolByName(context, 'portal_languages')
        self.languages = self.plt.getSupportedLanguages()

        # Hook
        self.set_up_parameters(context)

        fieldnames = self.metadata_fields + self.fields.keys()
        buffer = StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=fieldnames,
            dialect='bilbomatica')
        # cat = getToolByName(context, 'portal_catalog')

        query = ' '.join((
            self.query,
            "AND path_parents:({0})".format(' OR '.join(self.paths)),
        ))
        if "Language" not in query:
            query = ' ' .join((
                query, "AND +Language:({0})".format(' OR '.join(self.languages)),
            ))
        results = search_solr(query, **self.search_parameters)

        # results = cat(query)
        if len(results):
            writer.writerow(dict((fn, fn) for fn in fieldnames))
        nrows = 0
        for res in results:
            try:
                obj = res.getObject()
            except:
                log.warn("Could not get object for %{0}".format(res.getPath()))
                continue
            if self.skip_result(res, obj):
                continue
            data = self.get_metadata(res, obj)
            for fn, func in self.fields.items():
                value = obj.getField(fn).getAccessor(obj)()
                data[fn] = func(value)
            nrows += 1
            writer.writerow(data)
            if nrows >= self.limit:
                break


        csv_data = buffer.getvalue()
        buffer.close()

        return csv_data

    def get_metadata(self, brain, obj):
        data = dict(path=brain.getPath(), language=obj.Language())
        state = self.pwt.getInfoFor(obj, 'review_state')
        data['workflow_state'] = state
        data['creation_date'] = handleDate(obj.created())
        data['modification_date'] = handleDate(obj.modified())
        # Only export the first creator
        creators = obj.Creators()
        data['creator'] = handleString(len(creators) and creators[0] or '')
        return data

    def set_response_headers(self, response):
        response.setHeader(
            "Content-Disposition",
            "attachment; filename={0}.txt".format(self.name),
        )
        response.setHeader(
            "Content-Type", 'text/csv;charset=utf-8')


class NewsExporter(BaseExporter):
    name = 'news'
    limit = 500
    fields = OrderedDict([
        ('title', handleString),
        ('description', handleText),
        ('text', handleText),
        ('subject', handleList),
        ('country', handleList),
        ('multilingual_thesaurus', handleList),
    ])
    query = 'portal_type:("News Item") AND Language:any'

    def set_up_parameters(self, context):
        super(NewsExporter, self).set_up_parameters(context)
        self.search_parameters['sort'] = 'Date desc'
        # Debug: limit to teasers only
        # self.paths = [
        #     '/osha/portal/{0}/teaser'.format(lang) for lang in self.languages]

    def skip_result(self, brain, obj):
        # Don't export content if it is expired AND outdated
        if getattr(brain, 'outdated', False) and isExpired(brain):
            return True
        return False


class EventsExporter(BaseExporter):
    name = 'events'
    limit = 500
    fields = OrderedDict([
        ('title', handleString),
        ('description', handleText),
        ('text', handleText),
        ('startDate', handleDate),
        ('endDate', handleDate),
        ('dateToBeConfirmed', handleBool),
        ('location', handleString),
        ('attendees', handleList),
        ('eventUrl', handleString),
        ('contactName', handleString),
        ('contactEmail', handleString),
        ('contactPhone', handleString),
        ('subject', handleList),
        ('multilingual_thesaurus', handleList),
    ])
    query = 'portal_type:("Event") AND Language:any'


    def set_up_parameters(self, context):
        super(EventsExporter, self).set_up_parameters(context)
        self.search_parameters['sort'] = 'Date desc'

    def skip_result(self, brain, obj):
        # Don't export content if it is expired AND outdated
        if getattr(brain, 'outdated', False) and isExpired(brain):
            return True
        return False
