from persistent import Persistent
from zope.interface import implements
from zope.component import getUtility
from osha.policy.interfaces import IDatabaseSettings
from sqlalchemy.engine.url import URL
from sqlalchemy import Table
from sqlalchemy.orm import mapper, relation


class OSHADatabaseSettings(Persistent):

    implements(IDatabaseSettings)
    drivername = 'postgres'
    hostname = 'localhost'
    port = None
    username = ''
    password = None
    database = ''
