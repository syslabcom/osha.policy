from zope.interface import implements
from plone.app.workflow.interfaces import ISharingPageRole

from Products.CMFPlone import PloneMessageFactory as _

# These are for osha

class CheckerRole(object):
    implements(ISharingPageRole)

    title = _(u"title_can_check", default=u"Can check")
    required_permission = "Crosscheck portal content"
