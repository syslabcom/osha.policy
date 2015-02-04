import base64
import json
import logging

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import isExpired
from Products.Five.browser import BrowserView
from ZODB.POSException import POSKeyError
from plone.app.blob.field import BlobWrapper
from OFS.Image import File, Image


class JSONFeedView(BrowserView):
    """View for displaying the site rss feeds
    """

    def query(self):
        search = self.context.restrictedTraverse('@@language-fallback-search')
        url = getToolByName(self.context, 'portal_url')
        portal_path = url.getPortalPath()

        # Only use specific fields, so you can't do arbitrary queries.
        query = {
            'sort_on': 'effective',
            'sort_order': 'descending',
            'effective': {'query': DateTime(), 'range': 'max'},
        }
        form = self.request.form
        # required fields:
        for each in ['portal_type', 'Subject', 'path', 'Language']:
            query[each] = form[each]
        # optional fields:
        for each in ['object_provides']:
            query[each] = form.get(each, '')

        # start/end (also optional)
        if 'start' in form:
            query['end'] = {'query': DateTime(form['start']), 'range': 'min'}
        if 'end' in form:
            query['start'] = {'query': DateTime(form['end']), 'range': 'max'}

        query['path'] = portal_path + query['path']
        query['Subject'] = query['Subject'].split(',')
        q_size = form.get('q_size', 20)
        q_start = form.get('q_start', 0)

        brains = search.search(query)
        result = []

        for brain in brains[q_start:q_start + q_size]:
            if query['portal_type'] in ('News Item', 'Event', 'PressRelease') and (
                    getattr(brain, 'outdated', False) or isExpired(brain)):
                continue
            ob = brain.getObject()
            mapping = self._getMapping(ob)
            mapping['_type'] = ob.portal_type
            mapping['_path'] = url.getRelativeContentURL(ob)
            mapping['_url'] = ob.absolute_url()
            result.append(mapping)

        jsondata = json.dumps(result, encoding='UTF-8')
        #self.request.response.setHeader("Content-type", "application/json")
        #self.request.response.setHeader("Content-disposition","attachment;filename=hwcexport.json")
        return jsondata

    def _json_value(self, value):
        # Parts by Mikko Ohtamaa: thanks!
        if isinstance(value, DateTime):
            # Zope DateTime
            # http://pypi.python.org/pypi/DateTime/3.0.2
            return value.ISO8601()
        elif isinstance(value, (File, Image)):
            data = getattr(value, "data", None)
            if not data:
                return None
            if not isinstance(data, (str, unicode)):
                # A Pdata or similar object
                data = data.data
            return base64.b64encode(data)
        elif isinstance(value, BlobWrapper):
            try:
                data = value.data
                return base64.b64encode(data)
            except POSKeyError as e:
                logging.exception(e)
                return None
        else:
            # Let the JSON decoder deal with it.
            return value

    def _getMapping(self, ob):
        mapping = {}
        for field in ob.Schema().fields():
            name = field.getName()
            if field.type == 'blob':
                mapping[name] = ob.absolute_url()
                mapping['_%s_file_size' % name] = field.getRaw(ob).size()
            else:
                mapping[name] = self._json_value(field.getRaw(ob))
            if hasattr(field, 'getFilename'):
                filename = field.getFilename(ob)
                if filename:
                    mapping['_%s_filename' % name] = filename
                content_type = field.getContentType(ob)
                if content_type:
                    mapping['_%s_content_type' % name] = content_type
        return mapping
