import logging

from zope.component import queryUtility
from zope.app.container.interfaces import IObjectAddedEvent

from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.app.contentrules.rule import Rule

from plone.app.contentrules.actions import move 
from plone.app.contentrules.conditions import portaltype
from plone.app.contentrules.rule import get_assignments

from Products.CMFCore.utils import getToolByName

log = logging.getLogger('osha_centralisation_helper')

def run(self):
    ltool = getToolByName(self, 'portal_languages')
    langs = ltool.listSupportedLanguages()
    f = open('var/log/osha_centralisation.log', 'w')
    _centraliseNews(self, langs, f)
    _centraliseEvents(self, langs, f)
    f.close()
    return 'Done' 


def _centraliseEvents(self, langs, f):
    ls = [] 
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'Event',
                'path': path,
                }

        for l in self.portal_catalog(query):
            path = l.getPath()
            if  'teaser' in path or '/sub/riskobservatory' in path or  \
                '/campaigns/ew2005/comments/' in path or \
                '/campaigns/ew2006/accident_zone/' in path or \
                '/campaigns/ew2006/comments/' in path or \
                '/campaigns/ew2006/ideas_for_action/' in path or \
                '/campaigns/ew2007/accident_zone/' in path or \
                '/campaigns/ew2007/comments/' in path or \
                '/campaigns/ew2007/ideas_for_action/' in path or \
                '/campaigns/hw2008/ideas_action/' in path or \
                '/campaigns/hw2008/partners/' in path or \
                '/campaigns/hw2008/riskzone/' in path or \
                '/%s/events/' % lang in path:

                continue

            ls.append(l)

    items, parents = _setKeywords(ls, f)
    _assignContentRules(self, 'move-events-after-publish', f)
    _moveItemsToCentralLocation(self, items, f, 'events')


def _centraliseNews(self, langs, f):
    ls = [] 
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'News Item',
                'path': path,
                }

        for l in self.portal_catalog(query):
            path = l.getPath()
            if  'teaser' in path or '/sub/riskobservatory' in path or \
                '/campaigns/ew2005/comments/' in path or \
                '/campaigns/ew2006/accident_zone/' in path or \
                '/campaigns/ew2006/comments/' in path or \
                '/campaigns/ew2006/ideas_for_action/' in path or \
                '/campaigns/ew2007/accident_zone/' in path or \
                '/campaigns/ew2007/comments/' in path or \
                '/campaigns/ew2007/ideas_for_action/' in path or \
                '/campaigns/hw2008/ideas_action/' in path or \
                '/campaigns/hw2008/partners/' in path or \
                '/campaigns/hw2008/riskzone/' in path or \
                '/%s/news/' % lang in path:

                continue

            ls.append(l)

    items, parents = _setKeywords(ls, f)
    _assignContentRules(self, 'move-news-after-publish', f)
    _moveItemsToCentralLocation(self, items, f, 'news')


def _assignContentRules(self, rule_id, f):
    parents = [
        'en/campaigns/ew2006/',
        'en/campaigns/ew2007/',
        'en/campaigns/hw2008/',
        'en/campaigns/hwi/',
        'en/campaigns/hwi/',
        'en/campaigns/hwi/',
        'en/campaigns/hwi/',
        'en/good_practice/',
        'en/oshnetwork/member-states/belgium/events',
        'en/riskobservatory/',
        'en/topics/business/',
        ]

    storage = queryUtility(IRuleStorage)
    rule = storage.get(rule_id)
    portal_obj = self.portal_url.getPortalObject()
    for p in parents:
        parent = portal_obj.unrestrictedTraverse(p)
        # XXX Disabled for dry run...
        # assignments = IRuleAssignmentManager(parent, None)
        # get_assignments(storage[rule_id]).insert('/'.join(parent.getPhysicalPath()))
        # rule_ass = RuleAssignment(ruleid=rule_id, enabled=True, bubbles=True)
        # assignments[rule_id] = rule_ass
        f.write("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))
        log.info("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))


def _setKeywords(ls, f):
    parents = []
    items = []
    for l in ls:
        item = l.getObject() 
        items.append(item)
        parent = item.aq_parent
        subparent = False
        for p in parents:
            # we want to make a list of parents to which we assign content rules.
            # but we don't want to include subfolders because we'll let the content rule bubble.
            if p.absolute_url() in parent.absolute_url():
                subparent = True
                break
            elif parent.absolute_url() in p.absolute_url():
                parents.remove(p)
                 
        # if parent not in parents and not subparent:
        parents.append(parent)

        for fid, kw  in [ 
                ('ew2005', 'noise'), 
                ('ew2006', 'young_people'), 
                ('ew2007', 'msd'), 
                ('hw2008', 'risk_assessment'), 
                ('hwi', 'whp'),
                ('riskobservatory', 'risk_observatory'),
                ]:
            if fid in l.getPath():
                # item.setCategories(l.getCategories()+[kw])
                f.write("Add keyword '%s' to %s: %s \n" % (kw, l.portal_type, l.getPath()))
                log.info("Add keyword '%s' to %s: %s \n" % (kw, l.portal_type, l.getPath()))

    return items, parents


def _moveItemsToCentralLocation(self, items, f, folderpath):
    log.info('_moveItemsToCentralLocation')

    portal = self.portal_url.getPortalObject()
    for item in items:
        fullpath = '%s/%s' % (item.getLanguage() or 'en', folderpath)
        newfolder = portal.unrestrictedTraverse(fullpath)
        # cookie = item.aq_parent.manage_cutObjects(ids=[item.getId()])
        # newfolder.manage_pasteOjects(cookie)
        item_path = '/'.join(item.getPhysicalPath())
        f.write("'%s' now contains %s \n" % (fullpath, item_path))
        log.info("'%s', now contains %s \n" % (fullpath, item_path))
        # transaction.savepoint(optimistic=True)

