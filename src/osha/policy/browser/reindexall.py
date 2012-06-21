# -*- coding: utf-8 -*-

import transaction
from collective.solr.interfaces import ISolrIndexQueueProcessor
from Products.Five.browser import BrowserView
from Products.CMFCore.CMFCatalogAware import CatalogAware
from plone.app.async.interfaces import IAsyncService
from zope.component import getUtility, queryUtility
from DateTime import DateTime

import logging
logger = logging.getLogger('osha.policy.reindexall')


def reindex_async(context, path):
    """ sends a reindex request to the async queue """
    obj = context.restrictedTraverse(path)
    obj.reindexObject()
#    indexer = queryUtility(ISolrIndexQueueProcessor, name='solr')
#    indexer._index_and_commit(obj)


def job_failure_callback(result):
    logger.error(result)


class ReindexallView(BrowserView):

    def __call__(self):
        print "reindexall"
        global cnt, skipped

        modified = self.request.get('modified', '')
        modified_thresh = None
        if modified:
            try:
                modified_thresh = DateTime(modified)
            except:
                pass
        cnt = skipped = 0
        async = getUtility(IAsyncService)

        def handleItems(items):
            global cnt, skipped
            for item in items:
                id, obj = item
                if not isinstance(obj, CatalogAware):
                    continue
                if modified_thresh is not None:
                    if obj.modification_date < modified_thresh:
                        skipped += 1
                        continue

                path = "/".join(obj.getPhysicalPath())
                job = async.queueJob(reindex_async, self.context, path)
                callback = job.addCallbacks(failure=job_failure_callback)
                cnt += 1
                if cnt % 1000 == 0:
                    print "handled %d" % cnt

        res = self.context.ZopeFind(self.context, search_sub=1)
        res = [(self.context.getId(), self.context)] + res
        handleItems(res)
        status = "Handled a total of %(cnt)d items and skipped %(skipped)d " \
            "items based on modified-thrdeshold %(thresh)s" % dict(cnt=cnt,
            skipped=skipped, thresh=modified_thresh)
        print status
        return status
