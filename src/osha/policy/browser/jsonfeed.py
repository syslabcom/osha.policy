import base64
import json
import logging

from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ZODB.POSException import POSKeyError
from plone.app.blob.field import BlobWrapper

class JSONFeedView(BrowserView):
    """View for displaying the site rss feeds
    """
    
    def query(self):
        search = self.context.restrictedTraverse('@@language-fallback-search')
        url = getToolByName(self.context, 'portal_url')
        portal_path = url.getPortalPath()
        
        # Only use specific fields, so you can't do arbitrary queries.
        query = {'sort_on': 'effective', 'sort_order': 'descending'}
        form = self.request.form
        for each in ['portal_type', 'Subject', 'path', 'Language']:
            query[each] = form[each]
            
        query['path'] = portal_path + query['path']
        query['Subject'] = query['Subject'].split(',')
        
        q_size = form.get('q_size', 20)
        q_start = form.get('q_start', 0)
        
        brains = search.search(query)
        result = []
        for brain in brains[q_start:q_start+q_size]:
            ob = brain.getObject()
            mapping = self._getMapping(ob)
            mapping['_type'] = ob.portal_type
            mapping['_path'] = url.getRelativeContentURL(ob)
            mapping['_url'] = ob.absolute_url()
            result.append(mapping)
            
        jsondata = json.dumps(result, encoding='UTF-8')
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader("Content-disposition","attachment;filename=hwcexport.json")
        return jsondata

    def _json_value(self, value):
        # Thanks to Mikko Ohtamaa
        if isinstance(value, DateTime):
            # Zope DateTime
            # http://pypi.python.org/pypi/DateTime/3.0.2
            return value.ISO8601()
        elif hasattr(aq_base(value), "isBinary"):
            if value.isBinary():
                # Archetypes FileField and ImageField payloads
                # are binary as OFS.Image.File object
                data = getattr(value, "data", None)
                if not data:
                    return None
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
            mapping[name] = self._json_value(field.getRaw(ob))
            if hasattr(field, 'getFilename'):
                filename = field.getFilename(ob)
                if filename:
                    mapping['_%s_filename' % name] = filename
                content_type = field.getContentType(ob)
                if content_type:
                    mapping['_%s_content_type' % name] = content_type
        return mapping
        