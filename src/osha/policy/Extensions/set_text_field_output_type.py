from logging import getLogger

import transaction
from zope.app.component.hooks import getSite

logger = getLogger('osha.policy/set_text_field_output_type')


def main(self):
    portal = getSite()
    pc = portal.portal_catalog

    query = {
        "portal_type":[
            'RichDocument', 'Blog Entry', 'Document', 'RALink',
            'PressContact', 'PressRoom', 'HelpCenterFAQ', 'Event',
            'Topic', 'CallForContractors', 'PublicJobVacancy',
            'PressRelease', 'News Item', 'OSH_Link', 'SPSpeech']}

    results = pc._cs_old_searchResults(query)
    logger.info('Found %d results' % len(results))
    broken_brains = []
    for count, brain in enumerate(results):
        try:
            obj = brain.getObject()
            text_field = obj.Schema().getField("text")
        except Exception, e:
            broken_brains.append("%s: %s" %(brain.getPath(), e))
            continue
        if (text_field
            and hasattr(text_field, "default_output_type")
            and text_field.default_output_type == "text/x-html-safe"):
            text_field.default_output_type = "text/html"
            logger.info(
                "Set default_output_type on %s %s" %(
                    obj.portal_type, obj.absolute_url(1)))
        if count % 1000 == 0:
            transaction.commit()
            logger.info('Commited after %d items' % count)
    logger.info("Possibly invalid brains: %s" % broken_brains)
    transaction.commit()
    return "Done"
