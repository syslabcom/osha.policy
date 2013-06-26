from plone.app.linkintegrity.exceptions import \
    LinkIntegrityNotificationException
from plone import api
from Products.CMFCore.utils import getToolByName
from slc.linkcollection.interfaces import ILinkList
from zope.site.hooks import getSite

import logging
import re

logger = logging.getLogger('osha.policy.upgrades')


def rearrange_seps(context, items=None):
    """Rearrange SEPs with old accordeon layout in order to fit the new
    1-page layout which is SEO compliant.

    See #4153 for details.
    """
    portal = getSite()

    # added parameter 'items' to the method for easier testing
    if not items:
        items = [
            'en/topics/business-aspects-of-osh',
            'en/topics/maintenance',
            'en/topics/whp',
            'en/topics/economic-incentives',
            'en/riskobservatory',
        ]

    for item in items:
        default_page = portal.restrictedTraverse(item + '/index_html', None)

        if default_page:
            translations = [value[0] for value
                            in default_page.getTranslations().values()]

            logger.info('Rearranging SEPs for object: %s' % item)

            # process the object and all its translations
            for obj in translations:
                links = ILinkList(obj)

                try:
                    new_text = obj.getText()
                except UnicodeDecodeError:
                    logging.warning('Unicode error for: %s. Fix the ' \
                        'body text for this item and run the upgrade ' \
                        'step again.' % obj.absolute_url())
                    raise

                for url in links.urls:
                    if url.startswith('http'):
                        url = '/'.join(url.split('/')[4:])
                    else:
                        url = url[1:]
                    try:
                        linked = portal.restrictedTraverse(url)
                        new_text += ('<h2 class="linkcollection">%s</h2>%s' %
                                     (linked.Title(), linked.getText()))

                    except AttributeError:
                        # XXX: Some links appear to be missing?!
                        logging.warning('Error processing link: %s' % url)
                    except UnicodeDecodeError:
                        logging.warning('Unicode error for: %s. Fix the ' \
                            'body text for this item and run the upgrade ' \
                            'again.' % url)
                        raise
                    else:
                        try:
                            # delete linked item
                            linked.aq_parent.manage_delObjects(
                                [linked.getId()])
                        except LinkIntegrityNotificationException:
                            logging.warning("Not possible to delete %s " \
                                "because link integrity is violated" % url)

                # set new body text on the object and clear list of links
                obj.setText(new_text)
                links.urls = []
        else:
            logger.info('Rearranging SEPs for object: %s. No index_html '
                        'found.' % item)


def hide_contacts(context):
    """"Hide new-style contacts on all press releases by settting the field
    'showContacts' to False.

    We do this because we want to have this field True by default and we
    need to disable it for existing press releases, so that contact info
    is not shown twice on the template (contacts are now fetched from parent
    PressRoom object).

    See https://projects.syslab.com/issues/6105 for more info.
    """
    catalog = getToolByName(context, 'portal_catalog')
    press_releases = catalog(portal_type='PressRelease')

    logger.info('Setting showContacts to False for all press releases...')
    count = 0

    for release in press_releases:
        obj = release.getObject()
        setShowContacts = obj.getField('showContacts').getMutator(obj)
        setShowContacts(False)
        count = count + 1

    logger.info('%d press releases modified.' % count)


def lc_clear_database(context):
    """Delete portal_linkchecker/database so that the
    portal_linkchecker can be reinstalled
    #6952/#6977"""
    plc = getToolByName(context, 'portal_linkchecker')

    # To remove the database with the minimum of fuss we use _delOb
    # and then remove the entry from _objects
    plc._delOb("database")
    plc._objects = tuple([i for i in plc._objects if i["id"] != "database"])
    logger.info('The portal_linkchecker database has been cleared')


def reimport_actions(context):
    context.runImportStepFromProfile('profile-osha.policy:default',
                                     'actions')


def rearrange_blog(context):
    """Rearrange the blog section.

      * convert director's corner front-page from collection to page and set
        director-corner-view as the default layout (for all languages)
      * convert blog front-page from collection to page and set blog-view
        as the default layout (for all languages)

    See #6725 for details.
    """
    portal = api.portal.get()

    try:
        director_corner_en = portal['en']['about']['director_corner']
        dc_front_page_en = director_corner_en['front-page']
        blog_front_page_en = director_corner_en['blog']['front-page']
    except KeyError:
        logger.info('Rearrange blog: director corner or front pages not '
                    'found, nothing changed.')
        return

    dc_front_pages = dc_front_page_en.getTranslations(
        include_canonical=False).values()
    blog_front_pages = blog_front_page_en.getTranslations(
        include_canonical=False).values()

    # create new director's corner front pages for all languages
    logger.info('Rearrange blog: Converting director_corner/front-page from '
        'collection to page and setting director-corner-view as default '
        'layout (for all languages)...')
    new_dc_front_page_en = _convert_front_page(
        obj=dc_front_page_en,
        wf_state=api.content.get_state(obj=dc_front_page_en),
        layout='director-corner-view',
        fix_text=True
    )
    for front_page, wf_state in dc_front_pages:
        new_dc_front_page = _convert_front_page(
            obj=front_page,
            wf_state=wf_state,
            layout='director-corner-view',
            fix_text=True
        )
        new_dc_front_page.addTranslationReference(new_dc_front_page_en)

    # create new blog front pages for all languages
    logger.info('Rearrange blog: Converting director_corner/blog/front-page '
        'from collection to page and setting blog-view as default '
        'layout (for all languages)...')
    new_blog_front_page_en = _convert_front_page(
        obj=blog_front_page_en,
        wf_state=api.content.get_state(obj=blog_front_page_en),
        layout='blog-view'
    )
    for front_page, wf_state in blog_front_pages:
        new_blog_front_page = _convert_front_page(
            obj=front_page,
            wf_state=wf_state,
            layout='blog-view'
        )
        new_blog_front_page.addTranslationReference(new_blog_front_page_en)


def _convert_front_page(
        obj=None,
        wf_state=None,
        layout=None,
        fix_text=False):
    """Helper method for the rearrange_blog upgrade step to convert the
    front page object from Collection to Document.

    :param obj: front page object to convert to the Document type
    :param ws_state: workflow state of the object. If state is 'published',
        publish the object (private by default).
    :param layout: layout to set on the object
    :param fix_text: remove OSH blog description from body text, defaults to
        False (needed so we can use this method on blog and director corner
        front pages)
    :returns: new front page object
    :rtype: Document
    """
    if not obj or not wf_state or not layout:
        raise ValueError('You need to provide the obj, wf_state and layout '
                         'parameters.')

    folder = obj.getParentNode()

    # enable adding 'Document' objects to this folder
    allowed_types = folder.getLocallyAllowedTypes()
    if 'Document' not in allowed_types:
        folder.setLocallyAllowedTypes(allowed_types + ('Document',))

    title = obj.Title()
    text = obj.getText()

    # remove OSH Blog description from the body
    if fix_text:
        text = re.sub(
            re.compile('<h2>.{0,9}OSH Blog.*', re.DOTALL), '', text)

    folder._delOb(obj.getId())

    # create a new front-page
    folder.invokeFactory(
        'Document',
        'front-page',
        title=title,
        text=text,
    )

    new_obj = folder['front-page']

    # publish the object, if it was published before
    if wf_state == 'published':
        api.content.transition(obj=new_obj, transition='publish')

    # set the new layout
    new_obj.setLayout(layout)

    return new_obj
