# -*- coding: utf-8 -*-

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from plone.app.async.interfaces import IAsyncService
from zope.component import getUtility
from slc.linguatools import utils
from slc.outdated.adapter import ANNOTATION_KEY
from zope.annotation.interfaces import IAnnotatable, IAnnotations
import logging
log = logging.getLogger('osha.policy.cleanup')


ALLOWED_TYPES = (
    'News Item', 'Event', 'Document', 'RichDocument', 'PressRelease', 'Collage'
)
ALLOWED_ACTIONS = ('delete', 'make_private', 'make_outdated', 'make_expired')


def delete_item(context, path, id):

    obj = context.restrictedTraverse(path)
    info, warnings, errors = utils.exec_for_all_langs(
        obj, utils.delete_this, id_to_delete=id, target_id=id)


def make_private(context, path):
    obj = context.restrictedTraverse(path)
    info, warnings, errors = utils.exec_for_all_langs(
        obj, utils.workflow_action, transition='reject')


def make_expired(context, path):
    obj = context.restrictedTraverse(path)
    date = DateTime() - 1
    info, warnings, errors = utils.exec_for_all_langs(
        obj, expire_item, date=date)


def make_outdated(context, path):
    obj = context.restrictedTraverse(path)
    info, warnings, errors = utils.exec_for_all_langs(
        obj, outdate_item, outdated_status=True)


def job_failure_callback(result):
    log.warning(result)


def expire_item(ob, *args, **kw):
    """ Changes the object's workflow state
    """
    err = list()
    date = kw.get('date', None)
    if date and isinstance(date, DateTime):
        try:
            ob.setExpirationDate(date)
        except Exception, e:
            err.append(
                'Could not set expiration date on %s, error was: %s ' %
                (ob.absolute_url(), str(e)))
    return err


def outdate_item(ob, *arg, **kw):
    err = list()
    value = kw.get('outdated_status', None)
    value = not not value
    if IAnnotatable.providedBy(ob):
        IAnnotations(ob)[ANNOTATION_KEY] = value
    else:
        err.append(
            'Object %s does not support annotations' % ob.absolute_url())
    return err


class CleanupContent(BrowserView):

    def __call__(self):
        log.info('Called CleanupContent')
        cnt = 0
        action = self.request.get('action', '')
        if not action in ALLOWED_ACTIONS:
            return "You must supply an action parameter. Potential values: " \
                "%s" % ', '.join(ALLOWED_ACTIONS)
        threshold = self.request.get('threshold', '')
        try:
            date = DateTime(threshold)
        except:
            date = None
        if not threshold or not date:
            return "No valid value for parameter 'threshold' supplied. It " \
                "must represent a date"
        portal_type = self.request.get('portal_type', '')
        if portal_type not in ALLOWED_TYPES:
            return "You must supply a parameter 'portal_type'. Potential " \
                "values: %s" % ', '.join(ALLOWED_TYPES)

        plt = getToolByName(self, 'portal_languages')
        lang = plt.getPreferredLanguage()
        catalog = getToolByName(self, 'portal_catalog')
        parent_path = '/'.join(self.context.getPhysicalPath())
        query = dict(
            Language=[lang, ''], portal_type=portal_type,
            path=dict(query=parent_path, depth=-1),
        )
        date_param = dict(query=date, range='max')
        if portal_type in ('News Item', 'PressRelease', 'Collage'):
            query['effective'] = date_param
        elif portal_type == 'Event':
            query['end'] = date_param
        else:
            query['modified'] = date_param
        async = getUtility(IAsyncService)
        results = catalog(**query)
        for res in results:
            if action == 'delete':
                job = async.queueJob(
                    delete_item, self.context, parent_path, res.id)
            elif action == 'make_private':
                job = async.queueJob(make_private, self.context, res.getPath())
            elif action == 'make_expired':
                job = async.queueJob(make_expired, self.context, res.getPath())
            elif action == 'make_outdated':
                job = async.queueJob(
                    make_outdated, self.context, res.getPath())
            job.addCallbacks(failure=job_failure_callback)
            cnt += 1
        msg = "Handled a total of %d items of type '%s', action '%s'" % (
            cnt, portal_type, action)
        log.info(msg)
        return msg
