import logging
import transaction

from webdav.Lockable import ResourceLockedError

from zope import component
from zope.annotation.interfaces import IAnnotations

from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.engine.interfaces import IRuleAssignmentManager

from plone.app.contentrules.rule import get_assignments

from Products.CMFCore.utils import getToolByName

from p4a.subtyper.interfaces import ISubtyper

log = logging.getLogger('osha_centralisation_helper')

def run(self):
    ltool = getToolByName(self, 'portal_languages')
    langs = ltool.listSupportedLanguages()
    f = open('osha_centralisation.log', 'w')

    # NEWS
    # _setNewsKeywords(self, langs, f)
    # _assignContentRules(self, 'move-news-after-publish', f, langs)
    _centraliseNews(self, langs, f)

    # EVENTS
    # _setEventsKeywords(self, langs, f)
    # _assignContentRules(self, 'move-events-after-publish', f, langs)
    # _centraliseEvents(self, langs, f)

    f.close()
    return 'Done' 


def _setEventsKeywords(self, langs, f):
    log.info("_setEventsKeywords")
    ls = [] 
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'Event',
                'path': path,
                'Language': 'all',
                }

        ls += list(self.portal_catalog(query))

    _setKeywords(ls, f)


def _centraliseEvents(self, langs, f):
    log.info("_centraliseEvents")
    ls = []
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'Event',
                'path': path,
                'review_state': 'published',
                'Language': 'all',
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

    items = []
    for l in ls:
        try:
            item = l.getObject() 
        except:
            f.write("Couldn't get object! '%s'\n" % l.getPath())
            log.info("Couldn't get object! '%s'\n" % l.getPath())
            continue

        items.append(item)

    _moveItemsToCentralLocation(self, items, f, 'events')


def _setNewsKeywords(self, langs, f):
    log.info("_setNewsKeywords")
    ls = [] 
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'News Item',
                'path': path,
                'Language': 'all',
                }
        ls += list(self.portal_catalog(query))

    _setKeywords(ls, f)


def _centraliseNews(self, langs, f):
    log.info("_centraliseNews")
    ls = []
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'News Item',
                'path': path,
                'review_state': 'published',
                'Language': 'all',
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

    items = [l.getObject() for l in ls]
    _moveItemsToCentralLocation(self, items, f, 'news')


def _assignContentRules(self, rule_id, f, langs):
    log.info("_assignContentRules")
    for lang, dummy in langs:
        parents = [
            '%s/campaigns/ew2006/' % lang,
            '%s/campaigns/ew2007/' % lang,
            '%s/campaigns/hw2008/' % lang,
            '%s/campaigns/hwi/' % lang,
            '%s/good_practice/' % lang,
            '%s/oshnetwork/member-states/' % lang,
            '%s/topics/business/' % lang,
            '%s/riskobservatory/' % lang, 
            ]

        storage = component.queryUtility(IRuleStorage)
        rule = storage.get(rule_id)
        portal_obj = self.portal_url.getPortalObject()
        for p in parents:
            try:
                parent = portal_obj.unrestrictedTraverse(p)
            except:
                log.info("Couldn't find folder %s for adding content rule %s \n" % (parent.absolute_url(), rule_id))
                f.write("Couldn't find folder %s for adding content rule %s \n" % (parent.absolute_url(), rule_id))
                continue

            # XXX DOUBLE CHECK!!!!
            assignments = IRuleAssignmentManager(parent, None)
            get_assignments(storage[rule_id]).insert('/'.join(parent.getPhysicalPath()))
            rule_ass = RuleAssignment(ruleid=rule_id, enabled=True, bubbles=True)
            assignments[rule_id] = rule_ass
            f.write("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))
            log.info("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))


def _setKeywords(ls, f):
    log.info("_setKeywords")
    for l in ls:
        for fid, kw  in [ 
                ('ew2005', 'noise'), 
                ('ew2006', 'young_people'), 
                ('ew2007', 'msd'), 
                ('hw2008', 'risk_assessment'), 
                ('hwi', 'whp'),
                ('riskobservatory', 'risk_observatory'),
                ]:
            if fid in l.getPath():
                try:
                    item = l.getObject() 
                except:
                    f.write("Couldn't get object! '%s'\n" % l.getPath())
                    log.info("Couldn't get object! '%s'\n" % l.getPath())
                    continue

                try:
                    subject = item.getSubject()
                except:
                    subject = item.Schema().getField('subject').get(item)

                if kw not in subject:
                    subject = list(subject) + [kw]
                    item.setSubject(subject)
                    f.write("Add keyword '%s' to %s: %s \n" % (kw, l.portal_type, l.getPath()))
                    log.info("Add keyword '%s' to %s: %s \n" % (kw, l.portal_type, l.getPath()))
                else:
                    f.write("Keyword '%s' already in  %s: %s \n" % (kw, l.portal_type, l.getPath()))
                    log.info("Keyword '%s' already in %s: %s \n" % (kw, l.portal_type, l.getPath()))


def _subtypeAndConfigureOldParent(parent, portal_type, keywords):
    subtyper = component.getUtility(ISubtyper)
    if subtyper.existing_type(parent) is None:
        subtyper.change_type(parent, 'slc.aggregation.aggregator')
        if not parent.isCanonical():
            canonical = parent.getCanonical()
        else:
            canonical = parent

        subtyper.change_type(canonical, 'slc.aggregation.aggregator')
        annotations = IAnnotations(canonical)
        annotations['content_types'] =  [portal_type]
        annotations['review_state'] = 'published'
        annotations['aggregation_sources'] = ['/en/news']
        annotations['keyword_list'] = keywords
        annotations['restrict_language'] = False


def _moveItemsToCentralLocation(self, items, f, folderpath):
    log.info('_moveItemsToCentralLocation')

    portal = self.portal_url.getPortalObject()
    for item in items:
        fullpath = '%s/%s' % (item.getLanguage() or 'en', folderpath)
        newfolder = portal.unrestrictedTraverse(fullpath)
        parent = item.aq_parent
        try:
            subject = item.getSubject()
        except:
            subject = item.Schema().getField('subject').get(item)
        _subtypeAndConfigureOldParent(parent, item.portal_type, subject)
        try:
            cookie = parent.manage_cutObjects(ids=[item.getId()])
        except ResourceLockedError:
            item_path = '/'.join(item.getPhysicalPath())
            f.write("Could not copy '%s' to %s, locked by WEBDAV! \n" % (item_path, fullpath))
            log.info("Could not copy '%s' to %s, locked by WEBDAV! \n" % (item_path, fullpath))
            continue
            
        newfolder.manage_pasteObjects(cookie)
        item_path = '/'.join(item.getPhysicalPath())
        f.write("'%s' now contains %s \n" % (fullpath, item_path))
        log.info("'%s', now contains %s \n" % (fullpath, item_path))
        transaction.commit()

