# configure Linguaplone, don't do auto notification of outdated translations for speed reasons
# helps fixing #5676
from Products.LinguaPlone import config

import logging
logger = logging.getLogger('osha.policy')

was = config.AUTO_NOTIFY_CANONICAL_UPDATE
config.AUTO_NOTIFY_CANONICAL_UPDATE = 0
isnow = config.AUTO_NOTIFY_CANONICAL_UPDATE

logger.info('Configuring LinguaPlone AUTO_NOTIFY_CANONICAL_UPDATE. Was %s. Is now %s' % (was, isnow))
