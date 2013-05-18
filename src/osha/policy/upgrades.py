from plone.app.linkintegrity.exceptions import \
    LinkIntegrityNotificationException
from plone import api
from Products.CMFCore.utils import getToolByName
from slc.linkcollection.interfaces import ILinkList
from zope.site.hooks import getSite

import logging

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

      - move blog items from 'blog' subfolder to the parent folder
        (Director's corner)
      - convert front-page from collection to ordinary page and set blog-view
        as the default layout (for all languages)
      - delete blog subfolders in all languages (XXX: except in 'en',
        I'm experiencing errors when moving some of the items from blog folder
        to the parent folder [jcerjak])

    See #6725 for details.
    """
    portal = api.portal.get()

    try:
        director_corner = portal['en']['about']['director_corner']
    except KeyError:
        logger.info('Rearrange blog: director corner not found, nothing '
                    'changed.')
        return

    # move items to parent folder
    logger.info('Rearrange blog: Moving blog items to director corner...')

    for item in director_corner['blog'].listFolderContents():
        try:
            if item.id == 'front-page':
                del director_corner['blog']['front-page']
                continue
            api.content.move(source=item, target=director_corner)
        except AttributeError:
            # XXX: this happens on my local instance (jcerjak)
            logger.info(
                'Rearrange blog: cannot move object {0}, object does not '
                'exist'.format(item.absolute_url()))
        except LinkIntegrityNotificationException:
            logger.info(
                'Rearrange blog: cannot move object {0}, link integrity '
                'violated'.format(item.absolute_url()))

    # convert front-page to page type and set blog-view layout on it
    logger.info('Rearrange blog: Converting front-page from collection to '
                'page and setting blog-view as default layout (for all '
                'languages)...')
    front_page_en = director_corner.get('front-page')
    if front_page_en:
        description = front_page_en.Description()
        front_pages = front_page_en.getTranslations(
            include_canonical=False).values()

        # create a new canonical front page
        new_front_page_en = _convert_blog_front_page(
            obj=front_page_en,
            description=description,
            wf_state=api.content.get_state(obj=front_page_en)
        )

        # create new front pages for all languages, create translation
        # references and delete the blog subfolders
        for front_page, wf_state in front_pages:
            new_front_page = _convert_blog_front_page(
                obj=front_page,
                description=description,
                wf_state=wf_state
            )
            new_front_page.addTranslationReference(new_front_page_en)
            folder = new_front_page.getParentNode()

            # delete the blog subfolder, if it exists
            try:
                del folder['blog']
            except AttributeError:
                pass


def _convert_blog_front_page(obj=None, description=None, wf_state=None):
    """Helper method for the rearrange_blog upgrade step to convert the
    front page object from Collection to Document.

    :param obj: front page object to convert to the Document type
    :param description: description to set on the new front page object
    :param ws_state: workflow state of the object. If state is 'published',
        publish the object (private by default).
    :returns: new front page object
    :rtype: Document
    """
    folder = obj.getParentNode()
    title = obj.Title()
    # remove OSH Blog description from the body (it will be added to the
    # description)
    text = obj.getText().split('<h2>\r\n\tOSH Blog</h2>')[0]
    del folder['front-page']

    # create a new front-page
    folder.invokeFactory(
        'Document',
        'front-page',
        title=title,
        description=description,
        text=text,
    )
    new_obj = folder['front-page']

    # publish the object, if it was published before
    if wf_state == 'published':
        api.content.transition(obj=new_obj, transition='publish')

    # set blog view layout
    new_obj.setLayout('blog-view')

    return new_obj
