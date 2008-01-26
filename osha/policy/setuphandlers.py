import os, cPickle, logging, StringIO
from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
from Products.CMFCore.utils import getToolByName
from ConfigParser import ConfigParser
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES

basedir = os.path.abspath(os.path.dirname(__file__))
vocabdir = os.path.join(basedir, 'data', 'vocabularies')

def importVarious(context):
    if context.readDataFile("osha-various.txt") is None:
        return
    logger = logging.getLogger("osha.policy.setuphandler")
    logger.info("Importing OSHA specifics")
    
    site=context.getSite()
    
    quickinst = getToolByName(site, 'portal_quickinstaller')
    quickinst.installProduct('CMFPlacefulWorkflow')
    quickinst.installProduct('plone.browserlayer')
    quickinst.installProduct('plone.app.iterate')
    quickinst.installProduct('LinguaPlone')
    quickinst.installProduct('RichDocument')
    quickinst.installProduct('Clouseau')
    quickinst.installProduct('ATVocabularyManager')
    quickinst.installProduct('CallForContractors')
    quickinst.installProduct('FCKeditor')
    quickinst.installProduct('Marshall')
    quickinst.installProduct('OSHContentLink')
    quickinst.installProduct('PublicJobVacancy')
    quickinst.installProduct('PublicationProduct')
    quickinst.installProduct('collective.portlet.feedmixer')
    quickinst.installProduct('collective.portlet.tal')
    quickinst.installProduct('plone.portlet.collection')
    quickinst.installProduct('plone.portlet.static')
    quickinst.installProduct('VocabularyPickerWidget')
    #quickinst.installProduct('PressRoom')
#    quickinst.installProduct('webcouturier.dropdownmenu')
    


    quickinst.installProduct('ATCountryWidget')
    quickinst.installProduct('CMFSin')
    quickinst.installProduct('CaseStudy')
    quickinst.installProduct('DataGridField')
    quickinst.installProduct('TextIndexNG3')
    quickinst.installProduct('UserAndGroupSelectionWidget')
    quickinst.installProduct('simplon.plone.ldap')

    quickinst.installProduct('osha.theme')

    configurePortal(site)

    setVersionedTypes(site)

    addProxyIndexes(site)
    addExtraIndexes(site)
    
    importVocabularies(site)

#    catalog=getToolByName(site, 'portal_catalog')
#    index=catalog._catalog.getIndex("Language")
#    if index.numObjects()==0:
#        catalog.reindexIndex('Language', None)

def configurePortal(portal):
    """ make some changes to the portal config """
    getattr(portal.portal_types, 'Large Plone Folder').global_allow = True


def setVersionedTypes(portal):
    portal_repository = getToolByName(portal, 'portal_repository')
    versionable_types = list(portal_repository.getVersionableContentTypes())
    for type_id in ('RichDocument', 'Document'):
        if type_id not in versionable_types:
            versionable_types.append(type_id)
            # Add default versioning policies to the versioned type
            for policy_id in DEFAULT_POLICIES:
                portal_repository.addPolicyForContentType(type_id, policy_id)
    portal_repository.setVersionableContentTypes(versionable_types)


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
    
    # AvailableLanguages
    idx_id = "AvailableLanguages"
    if idx_id not in available:
        logger.info('Adding KeywordIndex %s' %idx_id)
        cat.manage_addProduct['PluginIndexes'].manage_addKeywordIndex(id=idx_id)

    # getExternal_url
    idx_id = "getExternal_url"
    if idx_id not in available:
        extra = dict()
        extra['default_encoding'] = 'utf-8'
        extra['languages'] = ['en']
        extra['splitter'] = 'oshlink.splitters.url_not_splitter'
        extra['index_unknown_languages'] = 1
        extra['splitter_casefolding'] = 1
    
        logger.info('Adding TextIndexNG3 %s' %idx_id)
        cat.manage_addProduct['TextIndexNG3'].manage_addTextIndexNG3(
            id = idx_id
          , extra = extra
          )


def addProxyIndexes(self):
    logger = logging.getLogger("OSHA.ProxyIndexes")
    logger.info("Adding Proxy Indexes")
    
    index_data = [
            { 'idx_id' : 'nace'
            , 'meta_id' : 'nace'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'country'
            , 'meta_id' : 'country'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'ero_country'
            , 'meta_id' : 'ero_country'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'cas'
            , 'meta_id' : 'cas'
            , 'extra' : dict(idx_type = "FieldIndex",
                )
            }
          , { 'idx_id' : 'multilingual_thesaurus'
            , 'meta_id' : 'multilingual_thesaurus'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'ero_target_group'
            , 'meta_id' : 'ero_target_group'
            , 'extra' : dict(idx_type = "FieldIndex",
                )
            }
          , { 'idx_id' : 'target_user_groups'
            , 'meta_id' : 'target_user_groups'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'category'
            , 'meta_id' : 'category'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
          , { 'idx_id' : 'html_meta_keywords'
            , 'meta_id' : 'html_meta_keywords'
            , 'extra' : dict(idx_type = "KeywordIndex",
                )
            }
        ]
    
    VALUE_EXPR = "python:object.getField('%(meta_id)s').getAccessor(object)()"
    
    cat = getToolByName(self, 'portal_catalog')
    available = cat.indexes()
    for data in index_data:
        if data['idx_id'] in available:
            continue
        extra = data['extra']
        extra['value_expr'] = VALUE_EXPR %{'meta_id': data['meta_id']}
        extra['key1'] = "indexed_attrs"
        extra['value1'] = "proxy_value"
        logger.info("Adding Proxy Index %s" % data['idx_id'])
        cat.manage_addProduct['ProxyIndex'].manage_addProxyIndex(
            id=data['idx_id'],
            extra=extra)
