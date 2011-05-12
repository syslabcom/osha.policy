#
# Copyright 2008, BlueDynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Jens Klein <jens@bluedynamics.com>"""              
__docformat__ = 'plaintext'

import AccessControl
import logging
import memcache
import random
from App.config import getConfiguration
from zope.security.interfaces import Unauthorized
from Products.PloneFlashUpload import ticket as pfuticket

logger = logging.getLogger('osha.policy')
logger.info('PATCHING PloneFlashUpload!')

def _getCache():
    config = getConfiguration()
    servers = config.product_config['flashuploader'].get('memcache-address')
    servers = servers.split(',')
    servers = [x.strip() for x in servers]
    client = memcache.Client(servers)
    return client

def _issueTicket(ident):
    """ issues a timelimit ticket 
    """
    ticket = str(random.random())
    sm = AccessControl.getSecurityManager()
    user = sm.getUser()
    if user is None:
        raise Unauthorized('No currently authenticated user')
    try:
        # see #28 — ticket handling: discrepancy in obtaining user's id
        # (issueTicket vs utils.find_user)
        uname = user.getName()
    except AttributeError:
        # <PropertiedUser 'admin'> has no getName(), thus we use getUserName()
        uname = user.getUserName()
    cache = _getCache()
    kw = {'ticket':ticket}
    cache.set(ident+ticket, uname)
    return ticket

if not getConfiguration().debug_mode:
    pfuticket.issueTicket = _issueTicket

def _validateTicket(ident, ticket):
    """validates a ticket
    """
    cache = _getCache()
    username = cache.get(ident+ticket)
    return username is not None

if not getConfiguration().debug_mode:
    pfuticket.validateTicket = _validateTicket

def _ticketOwner(ident, ticket):
    """Return username of the owner of the ticket.
    """
    cache = _getCache()
    username = cache.get(ident+ticket)
    return username

if not getConfiguration().debug_mode:
    pfuticket.ticketOwner = _ticketOwner

def _invalidateTicket(ident, ticket):
    """invalidates a ticket
    """
    cache = _getCache()
    username = cache.delete(ident+ticket)
    return username

if not getConfiguration().debug_mode:
    pfuticket.invalidateTicket = _invalidateTicket
