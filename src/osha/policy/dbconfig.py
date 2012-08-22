from App.config import getConfiguration
#import os, re
#import psycopg2
import Zope2
from logging import getLogger
from zope.app.publication.zopepublication import ZopePublication
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.registry import (
    field,
    Record,
)
from node.ext.ldap.interfaces import ILDAPProps
from pas.plugins.ldap.plonecontrolpanel.cache import REGKEY
from collective.solr.interfaces import ISolrConnectionConfig
from Products.CMFPlone.utils import getToolByName
from collective.tika.transforms import TIKA_TRANSFORMS
import transaction

configuration = getConfiguration()
if not hasattr(configuration, 'product_config'):
    conf = None
else:
    conf = configuration.product_config.get('osha.policy')
log = getLogger('osha.policy')

ROLES_DICT = {'users':          ['Member'],
              'administrators': ['Manager', 'TrackerManager'],
             }

def dbconfig(event):
    if conf is None:
        log.error('No product config found! Configuration will not be set')
        return
    db = Zope2.DB
    connection = db.open()
    root_folder = connection.root().get(ZopePublication.root_name, None)
    instancename = conf.get('ploneinstance_name')
    osha = root_folder.get('osha', None)
    plone = osha and osha.get('portal', None)
    if osha is None or plone is None:
        log.error('No Plone instance found! Create it manually ' \
        'with id %s and profile osha.policy' % instancename)
        # adding a Plone site without proper REQUEST is not supported
        return

    # LDAP
    pasldap = getattr(plone.acl_users, 'pasldap', None)
    # XXXX Deativated, since batou is not ready yet
    if False and pasldap is not None:
        ldapprops =  ILDAPProps(pasldap)
        if getattr(ldapprops, 'uri', '') != conf.get('ldap.uri', ldapprops.uri):
            ldapprops.uri = conf.get('ldap.uri', ldapprops.uri)
        if getattr(ldapprops, 'user', '') != conf.get('ldap.binddn', ldapprops.user):
            ldapprops.user = conf.get('ldap.binddn', ldapprops.user)
        if getattr(ldapprops, 'password','') != conf.get('ldap.bindpw', ldapprops.password):
            ldapprops.password = conf.get('ldap.bindpw', ldapprops.password)
    
        # memcached needs special handling
        reg = getUtility(IRegistry, context=plone)
        if REGKEY not in reg.records:
            # init if not exist
            value = field.TextLine(title=u'servers, delimited by space')
            reg.records[REGKEY] = Record(value)
        record = reg.records[REGKEY]
        if record.value != conf.get('memcached').decode('utf-8'):
            record.value = conf.get('memcached').decode('utf-8')
    # 
    #     log.debug('ldap config written')
    # 
    #     # can't do this in setuphandlers, because during site creation LDAP was
    #     # likely not set up yet
    # 
    #     groups_tool = getToolByName(plone, 'portal_groups')
    #     for groupid in ROLES_DICT:
    #         group = groups_tool.getGroupById(groupid)
    #         if group and False in [role in group.getRoles() \
    #                         for role in ROLES_DICT[groupid]]:
    #             roles = group.getRoles() + ROLES_DICT[groupid]
    #             groups_tool.editGroup(groupid, roles=roles, groups=())
    #     log.debug('groups set up')

    # Solr
    sm = plone.getSiteManager()
    solrcfgs = sm.getAllUtilitiesRegisteredFor(ISolrConnectionConfig)
    if not len(solrcfgs) == 0:
        solrcfg = solrcfgs[0]
        if getattr(solrcfg, 'host', '') != conf.get('solr.host', solrcfg.host):
            solrcfg.host = conf.get('solr.host', solrcfg.host)
        if getattr(solrcfg, 'port', '') != int(conf.get('solr.port', solrcfg.port)):
            solrcfg.port = int(conf.get('solr.port', solrcfg.port))
        if not getattr(solrcfg, 'active', None):
            solrcfg.active = True
        search_pattern = '(Title:{value}^5 OR Description:{value}^2 OR SearchableText:{value} OR SearchableText:({base_value}) OR searchwords:({base_value})^1000) showinsearch:True'
        if getattr(solrcfg, 'search_pattern', '') != search_pattern:
            solrcfg.search_pattern = search_pattern
        log.debug('solr config written')

    # Mail
    mailhost = getToolByName(plone, 'MailHost')
    if getattr(mailhost, 'smtp_host', '') != conf.get('mail.host', mailhost.smtp_host):
        mailhost.smtp_host = conf.get('mail.host')
    if getattr(mailhost, 'smtp_port', '') != conf.get('mail.port', mailhost.smtp_port):
        mailhost.smtp_port = conf.get('mail.port')
    if getattr(mailhost, 'smtp_uid', '') != conf.get('mail.user', mailhost.smtp_uid):
        mailhost.smtp_uid = conf.get('mail.user')
    if getattr(mailhost, 'smtp_pwd', '') != conf.get('mail.pass', mailhost.smtp_pwd):
        mailhost.smtp_pwd = conf.get('mail.pass')
    if mailhost.smtp_queue is not True:
        mailhost.smtp_queue = True
    if mailhost.smtp_queue_directory != conf.get('mail.queuedir', mailhost.smtp_queue_directory):
        mailhost.smtp_queue_directory = conf.get('mail.queuedir')
    log.debug('mail config written')

    # Transforms
    transforms = getToolByName(plone, 'portal_transforms')
    for name in TIKA_TRANSFORMS:
        trnsf = transforms.get(name)
        if not trnsf:
            # don't add transform if it's not there already, it has probably
            # been removed on purpose for migration
            continue
        if (not 'exec_prefix' in trnsf.get_parameters()) or \
          trnsf.get_parameter_value('exec_prefix') != conf.get('exec-prefix'):
            try:
                transforms.unregisterTransform(name)
                log.info("Removed transform %s" % name)
            except AttributeError:
                log.info("Could not remove transform - not found: %s" % name)
            except KeyError:
                if name in transforms.objectIds():
                    transforms._delObject(name, suppress_events=1)
                    log.info("Removed transform the hard way: %s" % name)
    
            transforms.manage_addTransform(name, 'collective.tika.transforms.' + name)
            log.info("New object added: %s" % name)
            trnsf = transforms.get(name)
    
        if trnsf.get_parameter_value('exec_prefix') != conf.get('exec-prefix'):
            trnsf.set_parameters(exec_prefix=conf.get('exec-prefix'))
    
    log.debug('transforms configured')


    # Memcached
    cache = plone.get('RAMCache', None)
    if not cache.__class__.__name__ == 'MemcachedManager':
        plone._delObject('RAMCache')
        plone.manage_addProduct['MemcachedManager'].manage_addMemcachedManager('RAMCache')
        cache = plone.get('RAMCache', None)
        log.debug('Replaced RAMCache with Memcached')
    settings = plone.get('RAMCache', None).getSettings()
    if settings['servers'] != [conf.get('memcached')]:
        settings['servers'] = [conf.get('memcached')]
        cache.manage_editProps('Memcached Manager', settings=settings)
    log.debug('memcached configured')


    transaction.commit()
