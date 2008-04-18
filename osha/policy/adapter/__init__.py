import logging
logger = logging.getLogger("osha.policy")

import schemaextender

# import lms retrievers if we have Linkchecker installed
try:
    import lmsretrievers
except:
    logger.info('Not importing LMS Retrievers. CMFLinkchecker not present?')
    