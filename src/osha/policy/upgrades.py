from slc.linkcollection.interfaces import ILinkList
from zope.site.hooks import getSite

import logging

logger = logging.getLogger('osha.policy.upgrades')


def rearrange_seps(context, items=None):
    """Rearrange SEPs with old accordeon layout in order to fit the new
    1-page layout which is SEO compliant.
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
                urls = ['/'.join(url.split('/')[4:]) for url in links.urls]
                new_text = ''

                for url in urls:
                    linked = portal.restrictedTraverse(url)
                    new_text += ('<h2 class="linkcollection">%s</h2>%s' %
                                 (linked.Title(), linked.getText()))

                    # delete linked item
                    linked.aq_parent.manage_delObjects([linked.getId()])

                # set new body text on the object and clear list of links
                obj.setText(new_text)
                links.urls = []
        else:
            logger.info('Rearranging SEPs for object: %s. No index_html '
                        'found.' % item)
