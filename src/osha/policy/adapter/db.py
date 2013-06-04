from logging import getLogger
from osha.policy.interfaces import IDatabaseSettings
from persistent import Persistent
from zope.interface import implements


log = getLogger("osha.policy")

class OSHADatabaseSettings(Persistent):

    implements(IDatabaseSettings)
    drivername = 'postgres'
    hostname = 'localhost'
    port = None
    username = ''
    password = None
    database = ''
