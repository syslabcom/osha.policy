import logging
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from slc.linguatools.utils import toggle_outdated

allowed_types = ['News Item', 'Event', 'Press Release']

logger = logging.getLogger('osha.policy.archiveOldContent')


def archiveByType(self, portal_type=None, age_in_days=None, limit=0):
    if not portal_type:
        return "You need to specify portal_type"
    if portal_type not in allowed_types:
        return "Only the following portal types are allowed: %s" %\
            ', '.join(allowed_types)
    if not age_in_days:
        return "You must provide age_in_days to indicate up to which day " \
            "content should become outdated. Example: age_in_days=180 for " \
            "6 months and older."
    try:
        days = int(age_in_days)
    except:
        return "The value passed for age_in_days is not a valid integer"
    try:
        limit = int(limit)
    except:
        return "The value passed for limit is not a valid integer"
    pc = getToolByName(self, 'portal_catalog')
    now = DateTime()
    date = now - days
    # hardcoded to corporate site
    query = dict(portal_type=portal_type,
        path="/osha/portal/en",
        Language='all',
        modified=dict(query=date, range='max'))
    res = pc(query)
    logger.info("I have %d results" % len(res))
    messages = list()
    if limit > 0:
        res = res[:limit]
    for r in res:
        try:
            obj = r.getObject()
        except:
            logger.warn("Error getting object for %s" % r.getPath())
            continue
        for lang in obj.getTranslations():
            trans = obj.getTranslation(lang)
            url = trans.absolute_url()
            logger.info('Handling item %s' % url)
            view = trans.restrictedTraverse('@@object_toggle_outdated')
            msg = view.toggle(True)
            msg += u" (<a href='%(url)s'>%(url)s</a>)" % dict(url=url)
            messages.append(msg)

    ret = "<html>%d objects were modified. The following actions were "\
        "performed:<ul><li>%s</ul></html>" %  \
        (len(messages), u"</li><li>".join(messages))
    return ret
