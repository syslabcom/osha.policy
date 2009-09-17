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

def run(self):
    ltool = getToolByName(self, 'portal_languages')
    langs = ltool.listSupportedLanguages()
    f = open('/home/zope/osha3/osha_centralisation_log.txt', 'w')
    centraliseNews(self, langs, f)
    centraliseEvents(self, langs, f)
    f.close()
    return 'Done' 

def _assignContentRules(parents, rule_id, f):
    storage = queryUtility(IRuleStorage)
    rule = storage.get(rule_id)
    for parent in parents:
        # XXX Disabled for dry run...
        # assignments = IRuleAssignmentManager(parent, None)
        # get_assignments(storage[rule_id]).insert('/'.join(parent.getPhysicalPath()))
        # rule_ass = RuleAssignment(ruleid=rule_id, enabled=True, bubbles=True)
        # assignments[rule_id] = rule_ass
        f.write("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))

def _setKeywords(ls, f):
    parents = []
    for l in ls:
        item = l.getObject() 
        parent = item.aq_parent
        if parent not in parents:
            parents.append(parent)

        for kw in ['ew2005', 'ew2006', 'ew2007', 'hw2008', 'hwi']:
            if kw in l.getPath():
                # item.setCategories(l.getCategories()+'ew2006')
                f.write("Add keyword '%s' to %s: %s \n" % (kw, l.portal_type, l.getPath()))

        if 'riskobservatory' in l.getPath():
            # item = l.getObject() 
            # item.setCategories(l.getCategories()+'ew2006')
            f.write("Add keyword '%s' to %s: %s \n" % ('risk_observatory', l.portal_type, l.getPath()))

    return parents

def centraliseEvents(self, langs, f):
    langs = [('en', 'dummy')]
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'Event',
                'path': path,
                }

        ls = [] 
        for l in self.portal_catalog(query):
            path = l.getPath()
            if 'teaser' in path or '/sub/riskobservatory' in path or '/%s/events/' % lang in path:
                continue

            ls.append(l)

        parents = _setKeywords(ls, f)
        _assignContentRules(parents, 'move-events-after-publish', f)


def centraliseNews(self, langs, f):
    langs = [('en', 'dummy')]
    for lang, dummy in langs:
        path = '/osha/portal/%s/' % lang
        query = {
                'portal_type': 'News Item',
                'path': path,
                }

        ls = [] 
        for l in self.portal_catalog(query):
            path = l.getPath()
            if 'teaser' in path or '/sub/riskobservatory' in path or '/%s/news/' % lang in path:
                continue

            ls.append(l)

        parents = _setKeywords(ls, f)
        _assignContentRules(parents, 'move-news-after-publish', f)



# rule_id = 'move-news-from-%s-to-global-news-folder' % parent.getId()
# rule = Rule()
# rule.title = \
#     "Move Published News from '%s' to the global News folder" % parent.pretty_title_or_id()
# rule.description = \
#     'Move Published News Items from this folder (%s) to the global News folder' % parent.pretty_title_or_id()
# rule.event = IObjectAddedEvent
# storage[rule_id] = rule
# XXX: Still not sure about this
