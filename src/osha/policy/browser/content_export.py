 # -*- coding: utf-8 -*-

# from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
# from Products.CMFPlone.utils import isExpired
from Products.Five.browser import BrowserView
from StringIO import StringIO
# from plone.app.async.interfaces import IAsyncService
# from zope.component import getUtility
# from slc.linguatools import utils
# from slc.outdated.adapter import ANNOTATION_KEY
# from zope.annotation.interfaces import IAnnotatable, IAnnotations
import csv
import logging
log = logging.getLogger('osha.policy.export')


csv.register_dialect(
    'bilbomatica', delimiter=';', doublequote=False, escapechar='\\',
    quoting=csv.QUOTE_ALL,
)


class BaseExporter(BrowserView):
    """Exports content into csv """

    query = ''
    limit = 10
    metadata_fields = [
        'path', 'Language',
    ]
    fields = []
    name = 'generic'

    def __call__(self):
        response = self.request.RESPONSE
        self.set_response_headers(response)
        return self.export_data()

    def export_data(self):
        context = self.context
        fieldnames = self.metadata_fields + self.fields
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
            data = dict(path=res.getPath(), Language=obj.Language())
            for fn in self.fields:
                data[fn] = obj.getField(fn).getAccessor(obj)()
            writer.writerow(data)

        csv_data = buffer.getvalue()
        buffer.close()

        return csv_data

    def set_response_headers(self, response):
        response.setHeader(
            "Content-Disposition",
            "attachment; filename={0}.txt".format(self.name),
        )
        response.setHeader(
            "Content-Type", 'text/csv;charset=utf-8')


class NewsExporter(BaseExporter):
    name = 'news'
    fields = ['title', 'description', 'subject', 'nace']
    query = dict(
        portal_type="News Item", Language="en")
