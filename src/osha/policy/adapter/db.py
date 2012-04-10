from persistent import Persistent
from zope.annotation.interfaces import IAnnotations
from zope.interface import implements
from zope.component import getUtility
from zope.app.component.hooks import getSite
from collective.lead import Database
from osha.policy.interfaces import IDatabaseSettings
import sqlalchemy
from sqlalchemy.engine.url import URL

SETTING_KEY = "osha.database.settings"


class Settings(Persistent):

    drivername = 'postgresql'
    hostname = 'localhost'
    port = None
    username = ''
    password = None
    database = ''


class OSHADatabaseSettings(Persistent):
    implements(IDatabaseSettings)

    @property
    def settings(self):
        site = getSite()
        ann = IAnnotations(site)
        return ann.setdefault(SETTING_KEY, Settings())

    def get_drivername(self):
        return self.settings.drivername
    def set_drivername(self, value):
        self.settings.drivername = value
    drivername = property(get_drivername, set_drivername)

    def get_hostname(self):
        return self.settings.hostname
    def set_hostname(self, value):
        self.settings.hostname = value
    hostname = property(get_hostname, set_hostname)

    def get_port(self):
        return self.settings.port
    def set_port(self, value):
        self.settings.port = value
    port = property(get_port, set_port)

    def get_username(self):
        return self.settings.username
    def set_username(self, value):
        self.settings.username = value
    username = property(get_username, set_username)

    def get_password(self):
        return self.settings.password
    def set_password(self, value):
        self.settings.password = value
    password = property(get_password, set_password)

    def get_database(self):
        return self.settings.database
    def set_database(self, value):
        self.settings.database = value
    database = property(get_database, set_database)

    # XXX We need a newer version of SQL-Alchemy for this to work
    # In the meantime, we still use the old collective.lead approach
    @property
    def connection(self):
        dsn = "%(driver)s://%(user)s:%(pwd)s@%(host)s:%(port)s/%(database)s" %\
        dict(driver=self.drivername, user=self.username, pwd=self.password,
        host=self.hostname, port=self.port, database=self.database)
        engine = sqlalchemy.create_engine(dsn, client_encoding='utf-8')
        conn = engine.connect()
        return conn


class OSHADatabase(Database):

    @property
    def _url(self):
        settings = getUtility(IDatabaseSettings)
        return URL(drivername=settings.drivername,
                    username=settings.username,
                    password=settings.password, host=settings.hostname,
                    port=settings.port, database=settings.database)

    def _setup_tables(self, metadata, tables):
        pass

    def _setup_mappers(self, tables, mappers):
        pass
