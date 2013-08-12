from plone.app.linkintegrity.exceptions import \
    LinkIntegrityNotificationException
from plone import api
from Products.CMFCore.interfaces._content import IDiscussionResponse
from Products.CMFCore.utils import getToolByName
from slc.linkcollection.interfaces import ILinkList
from zope.site.hooks import getSite
from plone.app.discussion.comment import CommentFactory
from plone.app.discussion.browser.migration import DT2dt
from plone.app.discussion.interfaces import IConversation, IReplies, IComment
from Acquisition import aq_parent

import logging
import re
import transaction

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


def migrate_comments(context):
    """Migrate comments to p.a.discussions

    Copies the p.a.discussion @@comment-migration view and adds some
    extra error handling
    """
    filter_callback = None
    context = getSite()
    out = []
    total_comments_migrated = [0]
    total_comments_deleted = [0]

    dry_run = False

    # This is for testing only.
    # Do not use transactions during a test.
    test = True

    if not test:
        transaction.begin()  # pragma: no cover

    catalog = getToolByName(context, 'portal_catalog')

    def log(msg):
        # encode string before sending it to external world
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')  # pragma: no cover
        context.plone_log(msg)
        out.append(msg)

    def migrate_replies(context, in_reply_to, replies, depth=0, just_delete=0):
        # Recursive function to migrate all direct replies
        # of a comment. Returns True if there are no replies to
        # this comment left, and therefore the comment can be removed.
        if len(replies) == 0:
            return True

        for reply in replies:

            # log
            indent = "  "
            for i in range(depth):
                indent += "  "
            log("%smigrate_reply: '%s'." % (indent, reply.title))

            should_migrate = True
            if filter_callback and not filter_callback(reply):
                should_migrate = False
            if just_delete:
                should_migrate = False

            new_in_reply_to = None
            if should_migrate:
                # create a reply object
                comment = CommentFactory()
                comment.title = reply.Title()
                comment.text = reply.cooked_text
                comment.mime_type = 'text/html'
                comment.creator = reply.Creator()

                email = reply.getProperty('email', None)
                if email:
                    comment.author_email = email

                comment.creation_date = DT2dt(reply.creation_date)
                comment.modification_date = DT2dt(reply.modification_date)

                comment.reply_to = in_reply_to

                if in_reply_to == 0:
                    # Direct reply to a content object
                    new_in_reply_to = conversation.addComment(comment)
                else:
                    # Reply to another comment
                    comment_to_reply_to = conversation.get(in_reply_to)
                    replies = IReplies(comment_to_reply_to)
                    try:
                        comment.text.encode("utf-8")
                        new_in_reply_to = replies.addComment(comment)
                    except UnicodeDecodeError, e:
                        log("Fixing UnicodeDecodeError %s" % e)
                        comment.text = comment.text.decode("utf-8")
                    new_in_reply_to = replies.addComment(comment)

            total_comments_migrated[0] += 1

            # migrate all talkbacks of the reply
            talkback = getattr( reply, 'talkback', None)
            no_replies_left = migrate_replies(context,
                                              new_in_reply_to,
                                              talkback.getReplies(),
                                              depth=depth+1,
                                              just_delete=not should_migrate)

            if no_replies_left:
                # remove reply and talkback
                talkback.deleteReply(reply.id)
                obj = aq_parent(talkback)
                obj.talkback = None
                log("%sremove %s" % (indent, reply.id))
                total_comments_deleted[0] += 1

        # Return True when all comments on a certain level have been
        # migrated.
        return True

    # Find content
    brains = catalog.searchResults(
        object_provides='Products.CMFCore.interfaces._content.IContentish',
        path={"query": "/osha/portal/en/about/director_corner"},
    )
    log("Found %s content objects." % len(brains))

    count_discussion_items = len(catalog.searchResults(
                                     Type='Discussion Item'))
    count_comments_pad = len(catalog.searchResults(
                                 object_provides=IComment.__identifier__))
    count_comments_old = len(catalog.searchResults(
                                 object_provides=IDiscussionResponse.\
                                     __identifier__))

    log("Found %s Discussion Item objects." % count_discussion_items)
    log("Found %s old discussion items." % count_comments_old)
    log("Found %s plone.app.discussion comments." % count_comments_pad)

    log("\n")
    log("Start comment migration.")

    # This loop is necessary to get all contentish objects, but not
    # the Discussion Items. This wouldn't be necessary if the
    # zcatalog would support NOT expressions.
    new_brains = []
    for brain in brains:
        if brain.portal_type != 'Discussion Item':
            new_brains.append(brain)

    # Recursively run through the comment tree and migrate all comments.
    for brain in new_brains:
        try:
            obj = brain.getObject()
            talkback = getattr( obj, 'talkback', None)
        except:
            log("There is no object for the brain at: %s" % brain.getPath())
            talkback = None
        if talkback:
            replies = talkback.getReplies()
            if replies:
                conversation = IConversation(obj)
            log("\n")
            log("Migrate '%s' (%s)" % (obj.Title(),
                                       obj.absolute_url(relative=1)))
            migrate_replies(context, 0, replies)
            obj = aq_parent(talkback)
            obj.talkback = None

    if total_comments_deleted[0] != total_comments_migrated[0]:
        log("Something went wrong during migration. The number of \
            migrated comments (%s) differs from the number of deleted \
            comments (%s)."  # pragma: no cover
             % (total_comments_migrated[0], total_comments_deleted[0]))
        if not test:  # pragma: no cover
            transaction.abort()  # pragma: no cover
        log("Abort transaction")  # pragma: no cover

    log("\n")
    log("Comment migration finished.")
    log("\n")

    log("%s of %s comments migrated."
        % (total_comments_migrated[0], count_comments_old))

    if total_comments_migrated[0] != count_comments_old:
        log("%s comments could not be migrated."
            % (count_comments_old - total_comments_migrated[0])) # pragma: no cover
        log("Please make sure your portal catalog is up-to-date.") # pragma: no cover

    if dry_run and not test:
        transaction.abort() # pragma: no cover
        log("Dry run") # pragma: no cover
        log("Abort transaction") # pragma: no cover
    if not test:
        transaction.commit() # pragma: no cover
    return '\n'.join(out)


def security_update(context):
    qi = api.portal.get_tool("portal_quickinstaller")
    
    for product in ("LoginLockout", "PasswordStrength"):
        if not qi.isProductInstalled(product):
            logger.info("Installing Products.%s" % product)
            qi.installProduct(product)

    au = api.portal.get_tool("acl_users")
    ps_plugin = au.password_strength_plugin
    ps_plugin.manage_changeProperties(p1_re=".{8}.*", p1_err="Minimum 8 characters.")
            
    logger.info("PasswordStrength configured.")
