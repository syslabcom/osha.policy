from zope.interface import Interface, alsoProvides
from zope import schema
from osha.theme import OSHAMessageFactory as _

class ISingleEntryPoint(Interface):
    """ A SEP which is identified by a keyword, can have its own skin, ...
    """    

class IDatabaseSettings(Interface):
    """ Settings to access the RDBMS """
    drivername = schema.ASCIILine(title=_(u"Driver name"), 
                   description=_(u"The database driver name"), 
                   default='mysql', 
                   required=True) 
    hostname = schema.ASCIILine(title=_(u"Host name"), 
                   description=_(u"The database host name"), 
                   default='localhost', 
                   required=True) 
                                
    port = schema.Int(title=_(u"Port number"), 
                   description=_(u"The database port number. " 
                                   "Leave blank to use the default."), 
                   required=False) 
    username = schema.ASCIILine(title=_(u"User name"), 
                   description=_(u"The database user name"), 
                   required=True) 
    password = schema.Password(title=_(u"Password"), 
                   description=_(u"The database password"), 
                   required=False) 
    database = schema.ASCIILine(title=_(u"Database name"), 
                   description=_(u"The name of the database on this server"), 
                   required=True) 
    