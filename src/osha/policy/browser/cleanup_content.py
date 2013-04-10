# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.app.async.interfaces import IAsyncService
from zope.component import getUtility
from slc.linguatools import utils
import logging
log = logging.getLogger('osha.policy.cleanup')


def delete_item(context, path, id):

    obj = context.restrictedTraverse(path)
    info, warnings, errors = utils.exec_for_all_langs(
        obj, utils.delete_this, id_to_delete=id, target_id=id)


def make_private(context, path):
    obj = context.restrictedTraverse(path)
    info, warnings, errors = utils.exec_for_all_langs(
        obj, utils.workflow_action, transition='reject')


def job_failure_callback(result):
    log.warning(result)


class CleanupContent(BrowserView):

    def __call__(self):
        log.info('Called CleanupContent')
        cnt = 0
        action = self.request.get('action', '')
        if not action in ('delete', 'make_private'):
            return "You must supply an action parameter. Potential values: " \
                "'delete' or 'make_private'"
        threshold = self.request.get('threshold', '')
        try:
            date = DateTime(threshold)
        except:
            date = None
        if not threshold or not date:
            return "No valid value for parameter 'threshold' supplied. It " \
                "must represent a date"
        portal_type = self.request.get('portal_type', '')
        if portal_type not in ('News Item', 'Event'):
            return "You must supply a parameter 'portal_type'. Potential " \
                "values: 'News Item' or 'Event'"

        plt = getToolByName(self, 'portal_languages')
        lang = plt.getPreferredLanguage()
        catalog = getToolByName(self, 'portal_catalog')
        parent_path = '/'.join(self.context.getPhysicalPath())
        query = dict(
            Language=[lang, ''], portal_type=portal_type,
            path=dict(query=parent_path, depth=-1),
        )
        date_param = dict(query=date, range='max')
        if portal_type == 'News Item':
            query['effective'] = date_param
        elif portal_type == 'Event':
            query['end'] = date_param
        async = getUtility(IAsyncService)
        results = catalog(**query)
        for res in results:
            if action == 'delete':
                job = async.queueJob(
                    delete_item, self.context, parent_path, res.id)
            elif action == 'make_private':
                job = async.queueJob(make_private, self.context, res.getPath())
            callback = job.addCallbacks(failure=job_failure_callback)
            cnt += 1
        msg = "Handled a total of %d items of type '%s', action '%s'" % (
            cnt, portal_type, action)
        log.info(msg)
        return msg
