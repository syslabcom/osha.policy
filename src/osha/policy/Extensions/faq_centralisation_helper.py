from copy import copy
import logging

from BeautifulSoup import BeautifulSoup, NavigableString

from zope import component
from zope.annotation.interfaces import IAnnotations
from zope.exceptions.interfaces import DuplicationError

from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleAssignmentManager
from plone.contentrules.engine.interfaces import IRuleStorage

from plone.app.contentrules.rule import get_assignments

from Products.AdvancedQuery import Or, Eq, And, In, Not
from Products.PloneHelpCenter.content.FAQFolder import HelpCenterFAQFolder
from Products.CMFCore.WorkflowCore import WorkflowException

from p4a.subtyper.interfaces import ISubtyper

log = logging.getLogger('faq_centralisation_helper')

QUESTION_TAGS = ["strong", "h3", "h2", "b"]

def run(self):
    # faqs = create_faqs_folder(self)
    # return 'done'
    portal = self.portal_url.getPortalObject()

    # Make the HelpCenterFAQ globally addable
    faq = portal.portal_types['HelpCenterFAQ']
    faq._updateProperty('global_allow', True)

    faq_folder = portal['en']['faq']
    constrain_addable_types(faq_folder)

    faq_docs = get_possible_faqs(self)
    
    import pdb; pdb.set_trace()
    parents = get_faq_containers(faq_docs)
    parse_and_create_faqs(self, faq_folder, faq_docs)
    return 'done'


def create_faqs_folder(self):
    """ There already exists a 'faq' folder in each of the language folders.
        For each of the language folders, rename it to faq-old, 
        and add a new HelpCenterFAQFolder with id faq.
    """
    log.info('create_faqs_folder')
    portal = self.portal_url.getPortalObject()
    en_folder = portal['en']
    if hasattr(en_folder, 'faq'):
        old_faq = en_folder.get('faq')
        en_folder.manage_renameObjects(['faq'], ['faq-old'])

    en_folder._setObject('faq', HelpCenterFAQFolder('faq'))
    faq = en_folder._getOb('faq')
    for lang in self.portal_languages.getSupportedLanguages():
        if lang == 'en' or not  hasattr(portal, lang):
            continue
        
        lang_folder = portal[lang]
        if hasattr(lang_folder, 'faq'):
            lang_folder.manage_renameObjects(['faq'], ['faq-old'])
            log.info('renamed faq to faq-old in %s' % lang)

        faq.addTranslation(lang)
    return faq
    

def get_possible_faqs(self):
    log.info('get_possible_faqs')
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



    # XXX: Didn't work :(
    # ls = self.portal_catalog(
    #             getId='faq.php',
    #             path='/osha/portal/en/good_practice/priority_groups/disability/')
    
    # XXX: Does not exist on production
    # ls = self.portal_catalog(
    #             getId='faq.stm',
    #             path='/osha/portal/en/good_practice/topics/dangerous_substances/')

    ls = self.portal_catalog(
                getId='faq.php',
                path='osha/en/good_practice/topics/accident_prevention/')

    log.info("Processing FAQs: %s" % "\n".join([i.getURL() for i in ls]))

    odict = {}
    for l in ls:
        o = l.getObject()
        odict[o.absolute_url()] = o
        ts = o.getTranslations().values()
        for t in ts:
            odict[t[0].absolute_url()] = t[0]

    objects = odict.values()
    return objects

    k = ['/'.join(o.getPhysicalPath()) for o in objects]
    k.sort()
    display_str = '\n'.join(k) or 'none'
    return display_str


def get_faq_containers(ls):
    log.info('get_faq_containers')
    parents = {}
    for l in ls:
        if l.portal_type == 'Folder':
            p = l
        else:
            p = l.aq_parent

        parents['/'.join(p.getPhysicalPath())] = p

    return parents

    display_str = '\n'.join([p.absolute_url() for p in parents.values()]) or 'none'
    return display_str


def create_faq(self, question_text, answer_text, state, faq_folder, obj, path=None):
    wf = self.portal_workflow
    faq_id = faq_folder.generateUniqueId()
    faqid = faq_folder.invokeFactory('HelpCenterFAQ', faq_id)
    faq = faq_folder.get(faqid)
    faq.setTitle(question_text)
    faq.setDescription(question_text)
    faq.setAnswer(answer_text)
    faq.setLanguage(obj.getLanguage())

    faq._renameAfterCreation(check_auto_id=False)
    faq.reindexObject()
    # # Set aliases
    # if path:
    #    rtool = self.portal_redirection
    #    rtool.addRedirect(path, '/'.join(faq.getPhysicalPath()))

    log.info('created faq: %s' % '/'.join(faq.getPhysicalPath()))

    if state == 'published':
        try:
            wf.doActionFor(faq, "publish")
        except WorkflowException:
            log.info('Could not publish the faq: %s' % '/'.join(faq.getPhysicalPath()))
            pass

    set_keywords(faq, obj.aq_parent)
    return faq
            

def parse_and_create_faqs(self, faq_folder, faq_docs):
    log.info('parse_and_create_faqs')
    wf = self.portal_workflow
    for obj in faq_docs:
        chain = wf.getChainFor(obj)
        status = self.portal_workflow.getStatusOf(chain[0], obj)
        state = status["review_state"]

        if obj.portal_type == 'Folder':
            QA_dict = parse_folder_faq(obj)
            for question_text, answer_text in QA_dict.values():
                correct_faq_folder = faq_folder.getTranslation(obj.getLanguage())
                create_faq(self, question_text, answer_text, state, correct_faq_folder, obj)

            # This is a one to one mapping.
            # Each RichTextDocument contains one Q and A and each maps to a
            # corresponding FAQ object.
            for doc in obj.objectValues():
                try:
                    wf.doActionFor(doc, "reject")
                except WorkflowException:
                    log.info('Could not reject the old faq: %s' % '/'.join(doc.getPhysicalPath()))

                old_title = doc.Title()
                if 'Migrated:' not in old_title:
                    doc.setTitle('Migrated: %s' % old_title)

                doc.reindexObject()

            obj.delProperty('layout')
            new_folder =  obj # We use the existing folder as our new aggregator

        else:
            QA_dict = parse_document_faq(obj)
            for question_text, answer_text in QA_dict.items():
                correct_faq_folder = faq_folder.getTranslation(obj.getLanguage())
                faq = create_faq(self, question_text, answer_text, state, correct_faq_folder, obj)

            if not QA_dict:
                log.info('No questions found for %s' % obj.absolute_url())
                continue

            # This is a one to many mapping.
            # One RichTextDocument with multiple Qs and As, that map to
            # multiple FAQ objects.
            try:
                wf.doActionFor(obj, "reject")
            except WorkflowException:
                log.info('Could not reject the old faq: %s' % '/'.join(obj.getPhysicalPath()))

            obj.setTitle('Migrated: %s' % obj.Title())
            obj.reindexObject()


            # We need to replace the document with a folder, that is subtyped
            # to slc.aggregator with an alias to the old document.
            obj_id = obj.getId()
            obj.aq_parent.manage_renameObjects([obj_id], ['%s-migrated' % obj_id])
            fid = obj.aq_parent.invokeFactory('Folder', obj_id)
            new_folder = obj.aq_parent.get(fid)


        new_folder.setTitle('Frequently Asked Questions')
        new_folder.reindexObject()

        subtype_container(new_folder)
        add_content_rule_to_container(new_folder)
        constrain_addable_types(new_folder)



def parse_folder_faq(folder):
    log.info('parse_folder_faq')
    QA_dict = {}
    faq_docs = folder.objectValues()
    for faq in faq_docs:
        if not faq.Title():
            continue # Ignore turds

        QA_dict['/'.join(faq.getPhysicalPath())] =  (faq.Title(), faq.getText())
    return QA_dict


def parse_document_faq(doc):
    log.info('parse_document_faq')
    QA_dict = {}
    body = doc.CookedBody()
    soup = BeautifulSoup(body)
    # Remove breadcrumb links
    for crumb in soup.findAll("p", {"class" : "crumb"}):
        if not crumb.contents:
            crumb.extract()
    for link in soup.findAll("a"):
        if link.has_key("href"):
            if link["href"] in ["#top", "."]:
                # Remove links to the top of the page
                link.extract()
        elif link.has_key("name"):
            # Remove anchors but keep the contents
            cnts = link.contents
            if " " in cnts:
                cnts.remove(" ")
            if len(cnts) == 0:
                link.extract()
            elif len(cnts) == 1:
                link.replaceWith(cnts[0])
            else:
                import pdb; pdb.set_trace()
                log.info(
                    "The anchor:%s contains more than one element"\
                    %unicode(link)
                    )

    possible_questions = []
    for tag in QUESTION_TAGS:
        possible_questions += soup.findAll(tag)

    probable_questions = []
    for question in possible_questions:
        if is_probable_question(question.parent):
            if " " in question.parent.contents:
                question.parent.contents.remove(" ")
            probable_questions += question.parent
        elif is_probable_question(question):
            probable_questions += question

    log.info("Probable Questions in this Document: %s"\
             %"\n".join([unicode(i) for i in probable_questions]))
    question_text = ''
    answer_text = ''
    for question in probable_questions:
        answer_text = ""
        if type(question) == NavigableString:
            question_text = unicode(question)
        else:
            question_text = unicode(question.findAll(text=True)[0])
            if len(question.findAll(text=True)) > 1:
                import pdb; pdb.set_trace()

        for answer in question.parent.nextSiblingGenerator():
            if is_probable_question(answer):
                break
            elif hasattr(answer , "name") and answer.name in ["h1", "h2", "h3"]:
                break
            else:
                answer_text += unicode(answer)

        while QA_dict.get(question_text):
            log.info('Duplicate question in QA_dict found')
            question_text += ' '

        # If there is no answer then it wasn't a question
        if answer_text and answer_text not in ["\n", " "]:
            # log.info("\nQ:%s\nA:%s" %(question_text, answer_text))
            QA_dict[question_text] = answer_text

    return QA_dict


def is_probable_question(suspect):
    # <h2>Q...
    # <h3>Q...
    # <p><strong>Q..
    # <p><b>Q..
    # endswith("?")

    if hasattr(suspect, "name"):
        if suspect.name in QUESTION_TAGS:
            suspect_text = suspect.findAll(text=True)[0]
            if suspect_text\
                   and suspect_text.strip().endswith("?"):
                return True

        elif suspect.name in ["a", "p"]:
            if hasattr(suspect, "contents"):
                # .contents returns a list of the subelements
                cnts = copy(suspect.contents)
                if " " in cnts:
                    cnts.remove(" ")
                if cnts:
                    first_item = cnts[0]
                    if hasattr(first_item, "name"):
                        if first_item.name in QUESTION_TAGS:
                            first_item_text = first_item.findAll(text=True)[0]
                            if first_item_text\
                                   and first_item_text.strip().endswith("?"):
                                return True
                                

def set_keywords(faq, old_parent):
    log.info("set_keywords")
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
        if fid in old_parent.getPhysicalPath():
            try:
                subject = faq.getSubject()
            except:
                subject = faq.Schema().getField('subject').get(old_parent)

            if kw not in subject:
                subject = list(subject) + [kw]
                faq.setSubject(subject)
                log.info("Add keyword '%s' to %s: %s \n" \
                        % (kw, faq.portal_type, faq.getPhysicalPath()))
            else:
                log.info("Keyword '%s' already in %s: %s \n" \
                        % (faq, faq.portal_type, faq.getPhysicalPath()))
                        
            log.info('Added keyword to FAQ %s, %s' % ('/'.join(faq.getPhysicalPath()), kw))

    faq.reindexObject()


def subtype_container(parent):
    subtyper = component.getUtility(ISubtyper)
    if subtyper.existing_type(parent) is None:
        subtyper.change_type(parent, 'slc.aggregation.aggregator')
        if not parent.isCanonical():
            canonical = parent.getCanonical()
        else:
            canonical = parent

        subtyper.change_type(canonical, 'slc.aggregation.aggregator')
        annotations = IAnnotations(canonical)
        annotations['content_types'] =  ['HelpCenterFAQ']
        annotations['review_state'] = 'published'
        annotations['aggregation_sources'] = ['/en/faq']
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
        log.info('%s subtyped as aggregator with keywords %s' % ('/'.join(parent.getPhysicalPath()), str(keywords)))


def add_content_rule_to_container(parent):
    log.info('add_content_rule_to_containers')
    # XXX: Change
    rule_id = 'rule-1'
    storage = component.queryUtility(IRuleStorage)
    rule = storage.get(rule_id)

    assignments = IRuleAssignmentManager(parent, None)
    get_assignments(storage[rule_id]).insert('/'.join(parent.getPhysicalPath()))
    rule_ass = RuleAssignment(ruleid=rule_id, enabled=True, bubbles=True)

    try:
        assignments[rule_id] = rule_ass
    except DuplicationError:
        log.info("Content Rule '%s'  was ALREADY assigned to %s \n" % (rule_id, parent.absolute_url()))
        
    log.info("Content Rule '%s' assigned to %s \n" % (rule_id, parent.absolute_url()))


def constrain_addable_types(parent):
    log.info('constrain_addable_types')
    parent.setConstrainTypesMode(True)
    parent.setLocallyAllowedTypes('HelpCenterFAQ')



