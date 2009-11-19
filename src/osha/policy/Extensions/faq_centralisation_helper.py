from copy import copy
import logging

from BeautifulSoup import BeautifulSoup, NavigableString

from zope import component
from zope.annotation.interfaces import IAnnotations

from Products.AdvancedQuery import Or, Eq, And, In, Not
from Products.PloneHelpCenter.content.HelpCenter import HelpCenter
from Products.CMFCore.WorkflowCore import WorkflowException

from p4a.subtyper.interfaces import ISubtyper

log = logging.getLogger('faq_centralisation_helper')

QUESTION_TAGS = ["strong", "h3", "h2", "b"]

def run(self):
    faqs = create_helpcenters(self)
    return 'done'

    portal = self.portal_url.getPortalObject()

    # Make the HelpCenterFAQ globally addable
    faq = portal.portal_types['HelpCenterFAQFolder']
    faq._updateProperty('global_allow', True)

    # Constrain the addable types to only HelpCenterFAQFolder, for the global
    # faq folders: i.e en/faq
    translations = portal['en']['faq'].getTranslations()
    for lang in translations:
        tfolder = translations[lang][0]
        tfolder.setConstrainTypesMode(True)
        tfolder.setLocallyAllowedTypes('HelpCenterFAQFolder')

    faq_docs = get_possible_faqs(self)

    # Each one of the faq_docs will become a HelpCenterFAQFolder
    # Each of the questions and answer combinations inside will become a
    # HelpCenterFAQ
    parse_and_create_faqs(self, faq_docs)
    return 'done'


def create_helpcenters(self):
    """ There already exists a 'faq' folder in each of the language folders.
        For each of the language folders, rename it to faq-old, 
        and add a new HelpCenter with id faq.
    """
    log.info('create_helpcenters')
    portal = self.portal_url.getPortalObject()
    en_folder = portal['en']
    if hasattr(en_folder, 'faq'):
        old_faq = en_folder.get('faq')
        en_folder.manage_renameObjects(['faq'], ['faq-old'])

    en_folder._setObject('faq', HelpCenter('faq'))
    log.info('created en/faq')
    faq = en_folder._getOb('faq')
    for lang in self.portal_languages.getSupportedLanguages():
        if lang == 'en' or not  hasattr(portal, lang):
            continue
        
        lang_folder = portal[lang]
        if hasattr(lang_folder, 'faq'):
            lang_folder.manage_renameObjects(['faq'], ['faq-old'])
            log.info('renamed faq to faq-old in %s' % lang)

        faq.addTranslation(lang)
        log.info('created %s/faq' % lang)
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
    
    ls = self.portal_catalog(
                getId='faq2.stm',
                path='osha/en/good_practice/topics/dangerous_substances/faq2.stm')

    # ls = self.portal_catalog(
    #             getId='faq.php',
    #             path='osha/en/good_practice/topics/accident_prevention/')

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


def create_helpcenter_faq_folders(self, QA_dict, global_faq_folder, obj):
    wf = self.portal_workflow
    chain = wf.getChainFor(obj)
    status = self.portal_workflow.getStatusOf(chain[0], obj)
    state = status["review_state"]

    for question_text, answer_text in QA_dict.items():
        correct_faq_folder = global_faq_folder.getTranslation(obj.getLanguage())
        # XXX: Beware, Title not always what we want...
        fid = correct_faq_folder.generateUniqueId()
        fid = correct_faq_folder.invokeFactory(
                            'HelpCenterFAQFolder', 
                            id=fid,
                            title=obj.Title()
                            )
        hcfaqfolder = correct_faq_folder._getOb(fid)
        create_faq(self, question_text, answer_text, state, hcfaqfolder, obj)


def decommision_old_faq(self, obj):
    """
    Mark wf state of the old FAQ as private
    Change it's id and title to indicate it's been migrated.
    Create a new folder with the original id and return it.
    """
    wf = self.portal_workflow
    try:
        wf.doActionFor(obj, "reject")
    except WorkflowException:
        log.info('Could not reject the old faq: %s' % '/'.join(obj.getPhysicalPath()))

    obj.setTitle('Migrated: %s' % obj.Title())
    obj_id = obj.getId()
    obj.aq_parent.manage_renameObjects([obj_id], ['%s-migrated' % obj_id])
    obj.reindexObject()

    # Create new folder with original id and return
    fid = obj.aq_parent.invokeFactory('Folder', obj_id)
    return obj.aq_parent.get(fid)


def parse_and_create_faqs(self, global_faq_folder, faq_docs):
    log.info('parse_and_create_faqs')

    for obj in faq_docs:
        if obj.portal_type == 'Folder':
            QA_dict = parse_folder_faq(obj)
        else:
            QA_dict = parse_document_faq(obj)

        if not QA_dict:
            log.warn('No questions found for %s' % obj.absolute_url())
            return

        create_helpcenter_faq_folders(self, QA_dict, global_faq_folder, obj)
        new_folder = decommision_old_faq(self)

        new_folder.setTitle('Frequently Asked Questions')
        new_folder.reindexObject()

        aggregator = subtype_container(new_folder)



def parse_folder_faq(folder):
    log.info('parse_folder_faq')
    QA_dict = {}
    faq_docs = folder.objectValues()
    for faq in faq_docs:
        if not faq.Title():
            continue # Ignore turds

        QA_dict[faq.Title()] = faq.getText()
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
            # XXX: suspect = '<h2></h2>'
            ls = suspect.findAll(text=True)
            if ls:
                suspect_text = ls[0]
            else:
                suspect_text = None

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
        annotations['content_types'] =  ['HelpCenterFAQFolder']
        annotations['review_state'] = 'published'
        annotations['aggregation_sources'] = ['/en/faq']
        keywords = []

        # The keyword we search for is the folder name of the single entry
        # point in which the aggregator is located.
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
        return parent





