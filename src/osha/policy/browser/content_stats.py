from zope.interface import implements
from zope.component import getMultiAdapter, getUtility 
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.lead.interfaces import IDatabase
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import logging
import Missing

logger = logging.getLogger('osha.policy/content_stats.py')
def log(text):
    logger.info(text)

class ContentStatisticsExportView(BrowserView):
    """ Writes object data relevant for statistics into external database """

    def __call__(self):
        log('Exporting statistical data')
        # open DB connection
        db = getUtility(IDatabase, name='osha.database')
        connection = db.connection 
        meta = sqlalchemy.MetaData()
        meta.bind = connection
        stats_table = sqlalchemy.Table('site_content_statistics_main', meta, autoload=True)
        subjects_table = sqlalchemy.Table('site_content_statistics_subject', meta, autoload=True)

        # get data from catalog
        cat = getToolByName(self.context, 'portal_catalog')
        res = cat(Language='all')

        n = 0
        # iterate through catalog data and write to DB
        for brain in res:
            obj_data = dict(uid = brain.UID,
                            portal_type = brain.portal_type,
                            creationdate = brain.CreationDate,
                            effectivedate = str(brain.EffectiveDate),
                            creator = brain.Creator,
                            getobjsize = brain.getObjSize,
                            language = brain.Language,
                            is_folderish = brain.is_folderish,
                            modificationdate = brain.ModificationDate,
                            review_state = brain.review_state
                           )
            for key in obj_data.keys():
                if obj_data[key] == Missing.Value:
                    obj_data[key] = None
                if obj_data[key] == 'None' or obj_data[key] == 'Unknown':
                    obj_data[key] = None
            ins = stats_table.insert(obj_data)
            result = connection.execute(ins)
            logger.debug(result)

            for subject in brain.Subject:
                subject_data = dict(uid = brain.UID,
                                    subject = subject
                                   )
                ins = subjects_table.insert(subject_data)
                result = connection.execute(ins)
                logger.debug(result)
            n = n + 1
            if n % 10000 == 0:
                log('%d items processed' % n)

        log('total %d items exported' % len(res))


