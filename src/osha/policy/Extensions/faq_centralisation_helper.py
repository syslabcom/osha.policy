import logging

from BeautifulSoup import BeautifulSoup

from zope import component
from zope.annotation.interfaces import IAnnotations

from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleAssignmentManager

from plone.app.contentrules.rule import get_assignments

from Products.AdvancedQuery import Or, Eq, And, In, Not

from p4a.subtyper.interfaces import ISubtyper

log = logging.getLogger('faq_centralisation_helper')

def run(self):
    faq_docs =  get_possible_faqs(self)
    parents = get_faq_containers(faq_docs)
    add_content_rule_to_containers(parents)
    subtype_containers(parents)
    set_keywords(parents)
    create_faqs(self, faq_docs)


def get_possible_faqs(self):
    queries = []
    title = In('Title', ["*frequently*", "*faq*", "FAQ*", "Frequently*"])
    portal_type = In("portal_type",  ["Document", "RichDocument", "Folder"])
    ids = ["faq", "faq.php", "faq.stm", "faqs"]
    for i in range(0, 10):
        ids.append('faq%d.stm' % i)
        ids.append('faq0%d.php' % i)

    id = In('getId', ids)
    body = Eq('SearchableText', "FAQ")
    fop = Eq('path', '/osha/portal/fop')
    advanced_query = And(Or(id, title, body), portal_type, Not(fop))

    ls =  self.portal_catalog.evalAdvancedQuery(advanced_query, (('Date', 'desc'),) ) 

    odict = {}
    for l in ls:
        o = l.getObject()
        odict[o.absolute_url()] = o
        ts = o.getTranslations().values()
        for t in ts:
            odict[t[0].absolute_url()] = t[0]

    objects = odict.values()

    k = ['/'.join(o.getPhysicalPath()) for o in objects]
    k.sort()
    display_str = '\n'.join(k) or 'none'
    return display_str


def get_faq_containers(ls):
    parents = {}
    for l in ls:
        p = l.aq_parent
        parents['/'.join(l.getPhysicalPath())] = p

    display_str = '\n'.join([p.absolute_url() for p in parents.values()]) or 'none'
    return display_str 


def add_content_rule_to_containers(parents):
    rule_id = 'rule-7'
    storage = component.queryUtility(IRuleStorage)
    rule = storage.get(rule_id)

    for parent in parents:
        assignments = IRuleAssignmentManager(parent, None)
        get_assignments(storage[rule_id]).insert('/'.join(parent.getPhysicalPath()))
        rule_ass = RuleAssignment(ruleid=rule_id, enabled=True, bubbles=True)

        assignments[rule_id] = rule_ass
        log.info("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))


def subtype_containers(parents):
    subtyper = component.getUtility(ISubtyper)
    for parent in parents:
        if subtyper.existing_type(parent) is None:
            subtyper.change_type(parent, 'slc.aggregation.aggregator')
            if not parent.isCanonical():
                canonical = parent.getCanonical()
            else:
                canonical = parent

            subtyper.change_type(canonical, 'slc.aggregation.aggregator')
            annotations = IAnnotations(canonical)
            annotations['content_types'] =  ['HelpCenterFAQFolder']
            annotations['review_state'] = 'published'
            annotations['aggregation_sources'] = ['/en/osha-help-center/faq']
            keywords = []
            for fid, kw  in [ 
                    ('disability', 'disability'),
                    ('young_people', 'young_people'),
                    ('agriculture', 'agriculture'), 
                    ('construction', 'construction'),
                    ('education', 'education'),
                    ('fisheries', 'fisheries'),
                    ('healthcare', 'healthcare'),
                    ('accident_prevention', 'accident_prevention'),
                    ('dangerous_substances', 'dangerous_substances'),
                    ('msds', 'msd'),
                    ('msd', 'msd'),
                    ]:

                if fid in parent.getPhysicalPath():
                    keywords.append(kw)

            annotations['keyword_list'] = keywords
            annotations['restrict_language'] = False


def set_keywords(parents):
    log.info("set_keywords")
    for p in parents:
        for fid, kw  in [ 
                ('disability', 'disability'),
                ('young_people', 'young_people'),
                ('agriculture', 'agriculture'), 
                ('construction', 'construction'),
                ('education', 'education'),
                ('fisheries', 'fisheries'),
                ('healthcare', 'healthcare'),
                ('accident_prevention', 'accident_prevention'),
                ('dangerous_substances', 'dangerous_substances'),
                ('msds', 'msd'),
                ('msd', 'msd'),
                ]:
            if fid in p.getPhysicalPath():
                try:
                    subject = p.getSubject()
                except:
                    subject = p.Schema().getField('subject').get(p)

                if kw not in subject:
                    subject = list(subject) + [kw]
                    p.setSubject(subject)
                    log.info("Add keyword '%s' to %s: %s \n" % (kw, item.portal_type, p.getPhysicalPath()))
                else:
                    log.info("Keyword '%s' already in %s: %s \n" % (kw, item.portal_type, p.getPhysicalPath()))


def create_faqs(self, faq_docs):
    faq_folder= self.en['osha-help-center']['faq']
    for doc in faq_docs:
        body = doc.CookedBody()
        soup = BeautifulSoup(body)

        faqs = []
        questions = self.soup.findAll("strong")
        for question in questions:
            question_text = question.contents[0]
            answer_text = question.parent.nextSibling.next.next
            faqid = faq_folder.invokeFactory('HelpCenterFAQ', doc.getId())
            faq = faq_folder.get(faqid)
            faq.setDescription(question_text)
            faq.setAnswer(answer_text)


