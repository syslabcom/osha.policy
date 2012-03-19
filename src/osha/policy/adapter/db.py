from persistent import Persistent 
from zope.interface import implements 
from zope.component import getUtility 
#from collective.lead import Database
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

# class OSHADatabase(Database): 
    
#     @property 
#     def _url(self): 
#         settings = getUtility(IDatabaseSettings) 
#         return URL(drivername=settings.drivername,  
#                     username=settings.username, 
#                     password=settings.password, host=settings.hostname, 
#                     port=settings.port, database=settings.database) 
                    
#     def _setup_tables(self, metadata, tables): 
#         pass
#         #tables['screening'] = Table('screening',  
#         #metadata, autoload=True) 
#         #tables['reservation'] = Table('reservation',  
#         #metadata, autoload=True) 

#     def _setup_mappers(self, tables, mappers): 
#         pass
