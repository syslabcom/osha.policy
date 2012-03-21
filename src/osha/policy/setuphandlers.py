import os
import cPickle
import logging
import transaction
from zope.app.component.hooks import getSite
from zope.component import getUtility

from AccessControl.Permission import registerPermissions
from ConfigParser import ConfigParser

from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
from Products.CMFCore.utils import getToolByName
# from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
from Products.ResourceRegistries.exportimport.resourceregistry import importResRegistry

from config import DEPENDENCIES, TYPES_TO_VERSION, DIFF_SUPPORT

logger = logging.getLogger("osha.policy.setuphandler")
basedir = os.path.abspath(os.path.dirname(__file__))
vocabdir = os.path.join(basedir, 'data', 'vocabularies')

def importVarious(context):
    if context.readDataFile("osha-various.txt") is None:
        return

    logger.info("Importing OSHA specifics")
    site=context.getSite()
    installDependencies(site)
    configurePortal(site)
    addProxyIndexes(site)
    addExtraIndexes(site)
    importVocabularies(site)
    # TODO: #4419
    # AttributeError: portal_countryutils
    #configureCountryTool(site)
    configureSEOOptimizer(site)
    # configureCacheFu(site)
    #modifySEOActionPermissions(site)
    repositionActions(site)
    # TODO: #4419
    # BadRequest: Error: invalid portal type
    # enableDiffSupport(site)

def installDependencies(site):
    qi = getToolByName(site, 'portal_quickinstaller')
    for product in DEPENDENCIES:
        if not qi.isProductInstalled(product):
            logger.info("Installing dependency: %s" % product)
            qi.installProduct(product)
            transaction.savepoint(optimistic=True)
    transaction.commit()

def repositionActions(portal):
    portal_actions=getToolByName(portal,'portal_actions')
    portal_conf=getToolByName(portal,'portal_controlpanel')
    cpids = [x.id for x in portal_conf.listActions()]
    # if xliff is installed, move site action xliff import into the object actions dropdown
    if getattr(portal_actions.site_actions, 'xliffimport', None):
        portal_actions.site_actions.xliffimport.visible = False
    # xliff import is re added in actions.xml
    # If SEO Tools are installed, move object action into the action dropdown
    # => nice to have, but a todo
    # # If Linkchecker is installed,
    # portal_linkchecker = getToolByName(portal, 'portal_linkchecker', None)
    # if portal_linkchecker:
    #     # move My Links to the user's dashboard
    #     if 'CMFLC_MyLinks' not in cpids:
    #         portal_conf.registerConfiglet( 'CMFLC_MyLinks'
    #              , 'My Links'
    #              , 'string:${portal_url}/lc_my_dead_links'
    #              , '''member'''
    #              , 'View'      # access permission
    #              , 'Member'
    #              , 1
    #              , 'CMFLinkChecker'
    #              , 'linkchecker.png'
    #              , 'The links owned by you.'
    #              , None
    #              )
        # move Links from the object tab into the actions dropdown
        # This happens in actions.xml

        # move link management site action into the actions dropdown
        # This happens in actions.xml

        # newactions = []
        # oldactions = portal_linkchecker.listActions()
        # for action in oldactions:
        #     if action.id in ['linkchecker_member_overview',
        #                      'linkchecker_object_status',
        #                      'linkchecker_balanced_scorecard']:
        #         action.visible = False
        #     newactions.append(action)
        # portal_linkchecker._actions = newactions


    # If Shoppinglist is installed, move it to the user's dashboard
    if 'Shoppinglist' not in cpids:
        portal_conf.registerConfiglet( 'Shoppinglist'
             , 'Shopping List'
             , 'string:${portal_url}/@@shoppinglistedit'
             , '''python:portal.portal_membership.checkPermission('Add portal content', object)'''
             , 'View'      # access permission
             , 'Member'
             , 1
             , 'slc.shoppinglist'
             , '++resource++shoppinglist_icon.gif'
             , 'Your shopping list which contains objects you have collected by adding them to your shopping list.'
             , None
             )
    # p4 upgrade: AttributeError: shoppinglistedit
    # portal_actions.user.shoppinglistedit.visible = False

    # compare site actions in the header with footer actions and remove duplications

    # I think this is not necessary - that's what the GS profile is for
#    portal_actions.footer_actions.disclaimer.i18n_domain='osha'
#    portal_actions.footer_actions.copyright.i18n_domain='osha'

    # move redirections nach object_buttons
    #if 'redirection' in portal_actions.object:
    #    cb = portal_actions.object.manage_cutObjects('redirection')
    #    portal_actions.object_buttons.manage_pasteObjects(cb)

    #if 'plone_setup' in portal_actions.object:
    #    cb = portal_actions.object.manage_cutObjects('plone_setup')
    #    portal_actions.object_buttons.manage_pasteObjects(cb)


def configurePortal(portal):
    """ make some changes to the portal config """
    portal_types = getToolByName(portal, 'portal_types')
    site_properties = getToolByName(portal, 'portal_properties').site_properties
    default_page = site_properties.getProperty('default_page')
    default_page += ('index.php','index.stm', 'index.stml')
    site_properties._updateProperty('default_page', default_page)

    portal._addRole('Checker')
    registerPermissions( [ ('Crosscheck portal content', None) ] )
    portal.manage_permission('Crosscheck portal content', roles=['Manager','Checker'], acquire=0)

    # remove LinguaLink from portal workflow chain
    portal_workflow = getToolByName(portal, 'portal_workflow')
    portal_workflow.setChainForPortalTypes(['LinguaLink'], None)

def resetJSRegistry(context):
    return importResRegistry(context, 'portal_javascripts',
                             'OSHA Javascript registry', 'osha-jsregistry.xml')

def importVocabularies(self):
    logger = logging.getLogger("VocabularyImporter")
    logger.info("Importing Vocabularies")
    vocabs = os.listdir(vocabdir)
    pvm = self.portal_vocabularies
    for vocabname in vocabs:
        vocabpath = os.path.join(vocabdir, vocabname)
        if vocabname.endswith('.vdex'):
            fh = open(vocabpath, "r")
            data = fh.read()
            fh.close()
            vocabname = vocabname[:-5]
            if vocabname in pvm.objectIds(): continue
            pvm.invokeFactory('VdexFileVocabulary', vocabname)
            pvm[vocabname].importXMLBinding(data)
            logger.info("VDEX Import of %s" % vocabname)

        elif vocabname.endswith('.dump'):
            fh = open(vocabpath, "r")
            data = fh.read()
            fh.close()
            vocabname = vocabname[:-5]
            if vocabname in pvm.objectIds(): continue
            vocabstruct = cPickle.loads(data)
            createSimpleVocabs(pvm, vocabstruct)
            logger.info("Dump Import of %s" % vocabname)


def addExtraIndexes(self):
    logger = logging.getLogger("OSHA.ExtraIndexes")
    logger.info("Adding Extra Indexes")

    cat = getToolByName(self, 'portal_catalog')
    available = cat.indexes()
    schema = cat.schema()

    # getRemoteProviderUID
    idx_id = 'getRemoteProviderUID'
    if idx_id not in available:
        logger.info('Adding KeywordIndex %s' %idx_id)
        cat.manage_addProduct['PluginIndexes'].manage_addKeywordIndex(id=idx_id, extra=dict(indexed_attrs=idx_id))

    #Additional Metadata
    META = ['getRemoteLanguage',
            'getCas',
            'getEinecs',
            'getRemoteUrl',
            'getRemoteProviderUID',
            'getMTSubject',
            'changefreq',
            'priority',
            'getLex_section',
            'getCountry',
            'getRa_contents',
            'getEROTarget_group',
            'getEROTopic'
            ]

    for meta in META:
        if meta not in schema:
            cat.manage_addColumn(meta)



    # getRemoteUrl
    idx_id = "getRemoteUrl"
    if idx_id not in available:
        extra = dict()
        extra['default_encoding'] = 'utf-8'
        extra['languages'] = ['en']
        extra['splitter'] = 'oshlink.splitters.url_not_splitter'
        extra['index_unknown_languages'] = 1
        extra['splitter_casefolding'] = 1

        logger.info('Adding TextIndexNG3 %s' %idx_id)
        # TODO: #4419
        # AttributeError: manage_addTextIndexNG3
        # cat.manage_addProduct['TextIndexNG3'].manage_addTextIndexNG3(
        #     id = idx_id
        #   , extra = extra
        #   )

    if 'getRemoteLanguage' not in available:
        logger.info('Adding KeywordIndex getRemoteLanguage')
        cat.manage_addProduct['PluginIndexes'].manage_addKeywordIndex(id='getRemoteLanguage', extra={'indexed_attrs': 'getRemoteLanguage'})


def addProxyIndexes(self):
    """ProxyIndex is no longer available, using KeywordIndex instead"""
    logger = logging.getLogger("OSHA.ProxyIndexes")
    logger.info("NOT adding Proxy Indexes - using Keyword / Field Indexes instead")

    keyword_index_data = [
            { 'idx_id' : 'nace'
            , 'meta_id' : 'nace'
            }
          , { 'idx_id' : 'country'
            , 'meta_id' : 'country'
            }
          , { 'idx_id' : 'multilingual_thesaurus'
            , 'meta_id' : 'multilingual_thesaurus'
            }
          , { 'idx_id' : 'ero_target_group'
            , 'meta_id' : 'ero_target_group'
            }
          , { 'idx_id' : 'target_user_groups'
            , 'meta_id' : 'target_user_groups'
            }
          , { 'idx_id' : 'subcategory'
            , 'meta_id' : 'subcategory'
            }
          , { 'idx_id' : 'ero_topic'
            , 'meta_id' : 'ero_topic'
            }
          , { 'idx_id' : 'lex_section'
            , 'meta_id' : 'lex_section'
            }
          , { 'idx_id' : 'occupation'
            , 'meta_id' : 'occupation'
            }
          , { 'idx_id' : 'osha_metadata'
            , 'meta_id' : 'osha_metadata'
            }
        ]
    field_index_data = [
          { 'idx_id' : 'cas'
            , 'meta_id' : 'cas'
            }
          , { 'idx_id' : 'isNews'
            , 'meta_id' : 'isNews'
            }
    ]


    cat = getToolByName(self, 'portal_catalog')
    available = cat.indexes()
    for data in keyword_index_data:
        if data['idx_id'] in available:
            continue
        logger.info("Adding Keyword Index %s" % data['idx_id'])
        cat.manage_addProduct['PluginIndexes'].manage_addKeywordIndex(id=data['idx_id'],
            extra=dict(indexed_attrs=data['idx_id']))

    for data in field_index_data:
        if data['idx_id'] in available:
            continue
        logger.info("Adding Field Index %s" % data['idx_id'])
        cat.manage_addProduct['PluginIndexes'].manage_addFieldIndex(id=data['idx_id'])


def configureCountryTool(site):
    """ Adds the relevant countries to the countrytool """
    ct = getToolByName(site, 'portal_countryutils')

    ct.manage_countries_reset()

    ct.manage_countries_addCountry('UK', 'United Kingdom')
    ct.manage_countries_addCountry('EU', 'Europa')
    ct.manage_countries_addCountry('EUO', 'Europa (others)')
    ct.manage_countries_addCountry('XX', 'International Organisation')

    ct.manage_countries_addArea('EU')
    ct.manage_countries_addCountryToArea('EU', ['EU', 'EUO', 'DK','FI','FR','IT','NL','PT','ES','UK', 'IE', 'LU', 'SE', 'AT', 'DE','MT', 'BE','CZ','HU','PL','RO','SK','BG','GR','SI','EE','LV','LT', 'CY'])
    ct.manage_countries_sortArea('EU')

    ct.manage_countries_addArea('International Organisations')
    ct.manage_countries_addCountryToArea('International Organisations', ['XX'])
    ct.manage_countries_sortArea('International Organisations')

    ct.manage_countries_addArea('Others')
    ct.manage_countries_addCountryToArea('Others', ['IS','LI','NO', 'CH','HR','BA','MK', 'AD', 'AE', 'AF', 'AG', 'AL', 'AM', 'AO', 'AQ', 'AR', 'AU', 'BR', 'CA', 'CL', 'CN', 'CO', 'CR', 'CU', 'EC', 'GL', 'HK', 'IL', 'IN', 'JO', 'JP', 'KR', 'KY', 'MS', 'MX', 'MY', 'NC', 'NZ', 'PE','PH', 'PK', 'PR', 'QA', 'RU', 'SA', 'SG', 'SH', 'SN', 'TH', 'TR', 'TW', 'US', 'UY', 'UZ', 'VE', 'VN', 'ZA', 'ZW'])
    ct.manage_countries_sortArea('Others')

def configureSEOOptimizer(site):
    """ set the parameters and actions """
    portalTypes = [ 'Folder'
                   ,'Topic'
                   ,'Blog Entry'
                   ,'CallForContractors'
                   ,'CaseStudy'
                   ,'Event'
                   ,'Link'
                   ,'News Item'
                   ,'OSH_Link'
                   ,'PressClip'
                   ,'PressContact'
                   ,'PressRelease'
                   ,'PressRoom'
                   ,'Provider'
                   ,'PublicJobVacancy'
                   ,'Publication'
                   ,'RichDocument'
                   ,'RALink'
                  ]
    pt = getToolByName(site, 'portal_types')
    for ptype in pt.objectValues():
        acts = filter(lambda x: x.id == 'seo_properties', ptype.listActions())
        action = acts and acts[0] or None

        if ptype.getId() in portalTypes:
            if action is None:
                ptype.addAction('seo_properties',
                                'SEO Properties',
                                'string:${object_url}/qseo_properties_edit_form',
                                '',
                                'Modify portal content',
                                'object',
                                visible=1)
        else:
            if action !=None:
                actions = list(ptype.listActions())
                ptype.deleteActions([actions.index(a) for a in actions if a.getId()=='seo_properties'])


def configureCacheFu(site):
    """ set osha specific caching rules
        this is specific for a CacheFu version.
        This needs to be adapted and re-tested for each new cache fu version
    """
    logger = logging.getLogger("osha.policy.setuphandler")
    logger.info("Configuring CacheFu")
    portal_cache_settings = getToolByName(site, 'portal_cache_settings', None)
    if portal_cache_settings is None:
        logger.info("CacheFu not installed, quitting.")
        return

    CFP = "default-cache-policy-v1.2"
    policy = getattr(portal_cache_settings, CFP, None)
    if policy is None:
        logger.warn("Policy not found. Has CacheFu been upgraded?")
        return
    rules = getattr(policy, 'rules')


    def _addToList(old_vals, new_vals):
        old_vals = list(old_vals)
        for item in new_vals:
            if item not in old_vals:
                old_vals.append(item)
        return old_vals

    #
    # Rule: Files & Images
    #
    downloads = getattr(rules, 'downloads')

    # Add Attached Filed and Attached Images to Types
    contentTypes = list(downloads.getTypes())
    new_types = ['FileAttachment', 'ImageAttachment']
    _addToList(contentTypes, new_types)
    downloads.setTypes(tuple(contentTypes))

    # Make Images and Files be cached in browser for 1 hour
    downloads.setHeaderSetIdExpression("python:object.portal_cache_settings.canAnonymousView(object) and 'cache-in-browser-1-hour' or 'no-cache'")

    #
    # Rule: plone-content-types
    #
    plone_content_types = getattr(rules, 'plone-content-types')

    # Remove Images and Files from the content cache rule
    # Add new types

    contentTypes = list(plone_content_types.getContentTypes())

    del_types = ['File', 'Image']
    for del_type in del_types:
        if del_type in contentTypes:
            contentTypes.remove(del_type)

    new_types = [ 'CallForContractors'
                , 'CaseStudy'
                , 'Event'
                , 'Favorite'
                , 'Link'
                , 'News Item'
                , 'OSH_Link'
                , 'Document'
                , 'PressClip'
                , 'PressContact'
                , 'PressRelease'
                , 'Provider'
                , 'Publication'
                , 'RichDocument'
                , 'RALink'
                , 'PublicJobVacancy'
                , 'Blog Entry'
                , 'HelpCenterDefinition'
                , 'HelpCenterErrorReference'
                , 'HelpCenterFAQ'
                , 'HelpCenterGlossary'
                , 'HelpCenterHowTo'
                , 'HelpCenterLink'
                , 'HelpCenterReferenceManualPage'
                , 'HelpCenterTutorialPage'
                , 'HelpCenterReferenceManual'
                , 'HelpCenterReferenceManualSection'
                , 'HelpCenterTutorial'
                , 'HelpCenterInstructionalVideo'
                , 'PloneboardComment'
                ]
    contentTypes = _addToList(contentTypes, new_types)
    plone_content_types.setContentTypes(tuple(contentTypes))

    # Set Cache header for anonymous to proxy 1h
    plone_content_types.setHeaderSetIdAnon('cache-in-proxy-1-hour')
    #
    # Rule: plone-containers
    #
    plone_containers = getattr(rules, 'plone-containers')

    # Add new types
    contentTypes = list(plone_containers.getContentTypes())

    new_types = [ 'Topic'
                , 'Folder'
                , 'Plone Site'
                , 'PressRoom'
                , 'PloneboardConversation'
                , 'PloneboardForum'
                , 'Ploneboard'
                , 'HelpCenterErrorReferenceFolder'
                , 'HelpCenterFAQFolder'
                , 'HelpCenter'
                , 'HelpCenterHowToFolder'
                , 'HelpCenterLinkFolder'
                , 'HelpCenterReferenceManualFolder'
                , 'HelpCenterTutorialFolder'
                , 'HelpCenterInstructionalVideoFolder'
                , 'b-org Project'
                ]
    contentTypes = _addToList(contentTypes, new_types)
    plone_containers.setContentTypes(tuple(contentTypes))

    # Set Cache header for anonymous to proxy 1h
    plone_containers.setHeaderSetIdAnon('cache-in-proxy-1-hour')

    # Set additional templates for folders
    templates = list(plone_containers.getTemplates())

    new_templates = [ 'good-practice-overview'
                    , 'teaser_view'
                    , 'sep_view'
                    ]

    templates = _addToList(templates, new_templates)
    plone_containers.setTemplates(tuple(templates))
    #
    # Rule: plone-templates
    #
    plone_templates = getattr(rules, 'plone-templates')

    # Set Cache header for anonymous to proxy 1h
    plone_templates.setHeaderSetIdAnon('cache-in-proxy-1-hour')

    # Set additional templates for templates
    templates = list(plone_templates.getTemplates())

    new_templates = [ 'rss-feeds'
                    ]
    templates = _addToList(templates, new_templates)
    plone_templates.setTemplates(tuple(templates))


def modifySEOActionPermissions(site):
    # And now update the relevant portal_type actions
    from Products.qSEOptimizer.Extensions.Install import qSEO_TYPES
    tool = getToolByName(site, 'portal_types')
    for ptype in tool.objectValues():
        #add the action for viewing versioning
        new_actions = []
        for action in ptype.listActions():
            if action.id == 'seo_properties':
                action.permissions = (u"Manage portal",)
            new_actions.append(action)
        ptype._actions = tuple(new_actions)

def setVersionedTypes(context):
    site = context.getSite()
    if context.readDataFile("osha-various.txt") is None:
        return

    portal_repository = getToolByName(site, 'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())
    for type_id in TYPES_TO_VERSION:
        if type_id not in versionable_types:
            # use append() to make sure we don't overwrite any
            # content-types which may already be under version control
            versionable_types.append(type_id)
            # Add default versioning policies to the versioned type
            # for policy_id in DEFAULT_POLICIES:
            #     portal_repository.addPolicyForContentType(type_id, policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)

def enableDiffSupport(site):

    portal_diff = getToolByName(site, 'portal_diff')
    diff_types = portal_diff.listDiffTypes()
    for type, field, diff in DIFF_SUPPORT:
        if type not in diff_types:
            portal_diff.manage_addDiffField(type, field, diff)



