import logging

from OFS.event import ObjectClonedEvent
from zExceptions import BadRequest

from zope import component
from zope.event import notify
from zope.lifecycleevent import ObjectCopiedEvent

from plone.portlet.collection import collection

from plone.portlets.constants import CONTEXT_CATEGORY
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
 
from plone.app.portlets.utils import assignment_mapping_from_key

from Products.CMFCore.utils import getToolByName
from Products.PlacelessTranslationService import getTranslationService

from p4a.subtyper.interfaces import ISubtyper
from osha.theme import portlets as osha_portlets

log = logging.getLogger('osha.policy/Extensions/create_member_states.py')

MEMBER_STATES = [
    "Denmark",
    "Bulgaria",
    "Czech Republic",
    "Germany",
    "Estonia",
    "Ireland",
    "Greece",
    "Spain",
    "France",
    "Italy",
    "Cyprus",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Hungary",
    "Malta",
    "Netherlands",
    "Austria",
    "Poland",
    "Portugal",
    "Romania",
    "Slovenia",
    "Slovakia",
    "Finland",
    "Sweden",
    "United Kingdom",
    "Iceland",
    "Liechtenstein",
    "Norway",
    "Switzerland",
    "Croatia",
    "The former Yugoslav Republic of Macedonia",
    "Turkey",
    "Albania",
    "Bosnia and Herzegovina",
    "Kosovo under UNSCR 1244/99",
    "Montenegro",
    "Serbia",
    ]

def run(self):
    """ """
    member_states = self.unrestrictedTraverse('en/oshnetwork/member-states')
    languages = self.portal_languages.getSupportedLanguages()
    if 'en' in languages:
        languages.remove('en')
    languages = ['en'] + languages

    for country_name in MEMBER_STATES:
        for lang in languages:
            country_folder = _create_country_folder(member_states, country_name, lang)
            #_add_language_tool(country_folder, country_name, languages)
            news_topic = _add_news_folder(country_folder, lang)
            events_topic = _add_events_folder(country_folder, lang)
            _add_index_html_page(country_folder, country_name, lang)
            _add_portlets(country_folder, news_topic, events_topic, lang)

    return 'Finished!'


def _create_country_folder(member_states, country_name, lang):
    log.info('_create_country_folder for %s in language: %s' \
             % (country_name, lang))
    sid = country_name.lower().replace(' ', '-').replace('/', '-')
    if member_states.portal_languages.getCanonicalLanguage() == lang:
        translate = getTranslationService().translate
        title_trans = translate(
                            target_language=lang, 
                            msgid=u'ew2000-navtitle_%s' % lang, 
                            default=country_name, 
                            context=member_states, 
                            domain='osha-subsites'
                            )
        try:
            member_states.invokeFactory('Folder', sid, title=title_trans)
        except BadRequest:
            log.info('Country folder %s already exists! Will take existing folder.' % country_name)

        country_folder = member_states._getOb(sid)

    else:
        canonical = member_states._getOb(sid)
        country_folder = canonical.addTranslation(lang)

    subtyper = component.getUtility(ISubtyper)
    subtyper.change_type(country_folder, 'slc.subsite.FolderSubsite')
    return country_folder


def _add_language_tool(country_folder, country_name, languages):
    log.info('_add_language_tool for %s' % country_name)
    tool = getToolByName(country_folder, 'portal_languages')
    newob = tool._getCopy(tool)
    newob._setId(tool.id)
    notify(ObjectCopiedEvent(newob, tool))

    country_folder._setOb(tool.id, newob)
    country_folder._objects = country_folder._objects+(dict(meta_type=tool.meta_type, id=tool.id),)

    ltool = country_folder._getOb(tool.id)
    ltool.wl_clearLocks()
    ltool._postCopy(country_folder, op=0)
    ltool.manage_afterClone(ltool)
    notify(ObjectClonedEvent(ltool))
    ltool.supported_langs = languages


def _add_news_folder(country_folder, lang):
    translate = getTranslationService().translate
    news_trans = translate(
                        target_language=lang, 
                        msgid=u'News', 
                        default=u'News', 
                        context=country_folder, 
                        domain='plone'
                        )
    log.info('_add_news_folder')
    if country_folder.portal_languages.getCanonicalLanguage() == lang:
        id = country_folder.invokeFactory('Folder', 'news', title=news_trans)
        news = country_folder._getOb(id)
    else:
        canonical_country_folder = country_folder.getCanonical()
        canonical_news = canonical_country_folder._getOb("news")
        news = canonical_news.addTranslation(lang)

    return _add_news_topic(news, lang)


def _add_events_folder(country_folder, lang):
    log.info('_add_events_folder')
    translate = getTranslationService().translate
    events_trans = translate(
                        target_language=lang, 
                        msgid=u'Events', 
                        default=u'Events', 
                        context=country_folder, 
                        domain='plone'
                        )
    if country_folder.portal_languages.getCanonicalLanguage() == lang:
        id = country_folder.invokeFactory('Folder', 'events', title=events_trans)
        events = country_folder._getOb(id)
    else:
        canonical_country_folder = country_folder.getCanonical()
        canonical_events = canonical_country_folder._getOb("events")
        events = canonical_events.addTranslation(lang)

    return _add_events_topic(events, lang)


def _add_index_html_page(country_folder, country_name, lang):
    if country_folder.portal_languages.getCanonicalLanguage() == lang:
        log.info('_add_index_html_page for %s' % country_name)
        try:
            country_folder.invokeFactory('Document', 'index_html', title=country_name)
        except BadRequest:
            log.info('index_html for  %s already exists! Will take existing folder.' % country_name)
            
        page = country_folder._getOb('index_html')
        try:
            page.manage_addProperty('layout', '@@oshnetwork-member-view', 'string')
        except BadRequest:
            log.info("Duplicate property '@@oshnetwork-member-view' for index_html of %s" % country_name)
        subtyper = component.getUtility(ISubtyper)
        subtyper.change_type(page, 'annotatedlinks')


def _add_portlets(obj, events_topic, news_topic, lang):
    log.info('_add_portlets for language %s' % lang)
    path = "/".join(obj.getPhysicalPath())
    oshabelow = assignment_mapping_from_key(obj, 'osha.belowcontent.portlets', CONTEXT_CATEGORY, path)

    events_topic_path = "/".join(events_topic.getPhysicalPath())
    news_topic_path = "/".join(news_topic.getPhysicalPath())

    translate = getTranslationService().translate
    news_trans = translate(
                        target_language=lang, 
                        msgid=u'News', 
                        default=u'News', 
                        context=obj, 
                        domain='plone'
                        )
    oshabelow[u'news-collection'] = collection.Assignment(
                                        header=news_trans,
                                        target_collection=news_topic_path,
                                        limit=5,
                                        )

    events_trans = translate(
                        target_language=lang, 
                        msgid=u'Events', 
                        default=u'Events', 
                        context=obj, 
                        domain='plone'
                        )
    oshabelow[u'events-collection'] = collection.Assignment(
                                        header=events_trans,
                                        target_collection=events_topic_path,
                                        limit=5,
                                        )

    rightcolumn_manager = component.getUtility(
                    IPortletManager,
                    name=u'plone.rightcolumn',
                    context=obj
                    )

    rightcolumn = component.getMultiAdapter(
                            (obj, rightcolumn_manager),
                            IPortletAssignmentMapping, context=obj
                            )

    rightcolumn[u'activities'] = osha_portlets.image.Assignment(
                                                            header=u"Agency's Activities",
                                                            image="/en/campaigns/hw2008/campaign/banner/hwp_en.swf",
                                                            )

    rightcolumn[u'links'] = osha_portlets.network_member_links.Assignment()


def _add_news_topic(news, lang):
    log.info('_add_news_topic for language: %s' %lang)
    if news.portal_languages.getCanonicalLanguage() == lang:
        id = news.invokeFactory('Topic', 'front-page')
        news_topic = news._getOb(id)
    else:
        canonical_news = news.getCanonical()
        canonical_topic = canonical_news._getOb("front-page")
        news_topic = canonical_topic.addTranslation(lang)

    # Add the Topic criteria
    effective_date = news_topic.addCriterion('effective', 'ATFriendlyDateCriteria')
    effective_date.setValue(0) # Set date reference to now
    effective_date.setOperation('less')

    expiration_date = news_topic.addCriterion('expires', 'ATFriendlyDateCriteria')
    expiration_date.setValue(0) # Set date reference to now
    expiration_date.setOperation('more')

    state = news_topic.addCriterion('review_state', 'ATSimpleStringCriterion')
    state.setValue('published')

    location = news_topic.addCriterion('path', 'ATRelativePathCriterion')
    location.setRelativePath('..')

    item_type = news_topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
    item_type.setValue('News Item')

    return news_topic


def _add_events_topic(events, lang):
    log.info('_add_events_topic for language: %s' %lang)
    if events.portal_languages.getCanonicalLanguage() == lang:
        id = events.invokeFactory('Topic', 'front-page')
        events_topic = events._getOb(id)
    else:
        canonical_events = events.getCanonical()
        canonical_topic = canonical_events._getOb("front-page")
        events_topic = canonical_topic.addTranslation(lang)


    # Add the Topic criteria
    item_type = events_topic.addCriterion('portal_type', 'ATSimpleStringCriterion')
    item_type.setValue('Event')

    state = events_topic.addCriterion('review_state', 'ATSimpleStringCriterion')
    state.setValue('published')

    effective_date = events_topic.addCriterion('effective', 'ATFriendlyDateCriteria')
    effective_date.setValue(0) # Set date reference to now
    effective_date.setOperation('less')

    expiration_date = events_topic.addCriterion('expires', 'ATFriendlyDateCriteria')
    expiration_date.setValue(0) # Set date reference to now
    expiration_date.setOperation('more')

    location = events_topic.addCriterion('path', 'ATRelativePathCriterion')
    location.setRelativePath('..')

    return events_topic



