from plone.app.linkintegrity.exceptions import \
    LinkIntegrityNotificationException
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

