 # -*- coding: utf-8 -*-

# from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
# from Products.CMFPlone.utils import isExpired
from Products.Five.browser import BrowserView
from StringIO import StringIO
# from plone.app.async.interfaces import IAsyncService
# from zope.component import getUtility
# from slc.linguatools import utils
# from slc.outdated.adapter import ANNOTATION_KEY
# from zope.annotation.interfaces import IAnnotatable, IAnnotations
from ordereddict import OrderedDict

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
    metadata_fields = [
        'path', 'language', 'creation_date', 'modification_date', 'creator'
    ]
    fields = []
    name = 'generic'

    def __call__(self):
        response = self.request.RESPONSE
        self.set_response_headers(response)
        return self.export_data()

    def export_data(self):
        context = self.context
        fieldnames = self.metadata_fields + self.fields.keys()
        buffer = StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=fieldnames,
            dialect='bilbomatica')
        cat = getToolByName(context, 'portal_catalog')
        results = cat(self.query)
        if len(results):
            writer.writerow(dict((fn, fn) for fn in fieldnames))
        for res in results[:self.limit]:
            try:
                obj = res.getObject()
            except:
                log.warn("Could not get object for %{0}".format(res.getPath()))
                continue
            data = self.get_metadata(res, obj)
            for fn, func in self.fields.items():
                value = obj.getField(fn).getAccessor(obj)()
                data[fn] = func(value)
            writer.writerow(data)

        csv_data = buffer.getvalue()
        buffer.close()

        return csv_data

    def get_metadata(self, brain, obj):
        data = dict(path=brain.getPath(), language=obj.Language())
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
    query = dict(
        portal_type="News Item", Language="en")


class EventExporter(BaseExporter):
    name = 'event'
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
    query = dict(
        portal_type="Event", Language="en")
