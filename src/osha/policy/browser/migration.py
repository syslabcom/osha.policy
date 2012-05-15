import transaction
from zope.app.component.hooks import getSite
import logging
import traceback
import transaction
from cStringIO import StringIO

from types import *
from datetime import datetime

from Products.Five import BrowserView

from Acquisition import aq_inner, aq_parent, aq_base, aq_chain, aq_get
from Products.CMFCore.utils import getToolByName

from Products.contentmigration.basemigrator.walker import Walker
from plone.app.blob.migrations import ATImageToBlobImageMigrator

root_ids =     [    'portal_setup', 'MailHost', 'content_type_registry', 'error_log',    'plone_utils', 'portal_actionicons', 'portal_actions',    'portal_atct', 'portal_controlpanel', 'portal_css', 'portal_diff',    'portal_discussion', 'portal_factory', 'portal_groupdata',    'portal_groups', 'portal_interface', 'portal_javascripts',    'portal_kss', 'portal_memberdata', 'portal_membership',    'portal_metadata', 'portal_migration', 'portal_password_reset',    'portal_properties', 'portal_quickinstaller',    'portal_registration', 'portal_skins', 'portal_syndication',    'portal_types', 'portal_uidannotation', 'portal_uidgenerator',    'portal_undo', 'portal_url', 'portal_view_customizations',    'portal_workflow', 'translation_service',    'portal_form_controller', 'mimetypes_registry',    'portal_transforms', 'archetype_tool', 'reference_catalog',    'uid_catalog', 'acl_users', 'kupu_library_tool',    'portal_archivist', 'portal_historiesstorage',    'portal_historyidhandler', 'portal_modifier',    'portal_purgepolicy', 'portal_referencefactories',    'portal_repository', 'portal_uidhandler', 'portal_languages',    'RAMCache_RAM', 'ResourceRegistryCache', 'Members',    'portal_placeful_workflow', 'marshaller_registry',    'portal_countryutils', 'sin_tool', 'portal_vocabularies', 'data',    'en', 'bg', 'cs', 'da', 'nl', 'et', 'fi', 'fr', 'de', 'el', 'hu',    'it', 'lv', 'lt', 'mt', 'pl', 'pt', 'ro', 'sk', 'sl', 'es', 'sv',    'ReindexHelper', 'images', 'reindexThis', 'tr', 'no', 'ownertest',    'ReindexHelperPath', 'new-case-study', 'perftest',    '.wf_policy_config', 'portal_calendar', 'tmp',    'portal_alertservice', 'portal_ploneboard', 'hr',    'google_test_cse3', 'index_html', 'eopro', 'directory',    'CacheSetup_ResourceRegistryCache_RAM', 'portal_redirection',    'sql', 'subscriptions.js', 'scripts', 'logo_small.gif',    'google9f3b856e9891b67d.html', 'googleef20cdffcecd6736.html',    'google532cc25ad07b2121.html', 'persistSiteMap',    'googlec8582979cf35e207.html', 'default_error_message',    'checkUnmigratedNace', 'checklist_hotels_data',    'sitemap_1.xml.gz', 'sitemap_index.xml.gz', 'osha',    'MemcachedManager', 'RAMCache', 'lists-database',    'napofilmstructure', 'getRID', 'sub', 'airliquide.jpg',    'baxter.jpg', 'copy_of_baxter.jpg', 'cesi.jpg', 'efnms.jpg',    'epsc.jpg', 'ge.jpg', 'imaginationatwork.jpg', 'lilly.jpg',    'ima.jpg', 'copy_of_efnms.jpg', 'reporting', 'LCRetrieveByDate',    'fop', 'sitemap_2.xml.gz', 'SCRIPTS', 'cleanNewOshEraCat',    'fixImportTags', 'uniqueValuesForSubject', 'cleanWordPastedText',    'LCRetrieveByPath', 'lcregisterThis', 'topbannerwos.jpg',    'google', 'portal_cache_settings', 'portal_squid', 'formgen_tool',    'relations_library', 'getUID', 'set_uploaded_file_titles.bak',    'resource_centralisation_helper', 'exchangeSEPPortlets',    'checkMemberFoldersForOSHLinks', 'testpubbysubject', 'test',    'test_em', 'checkFinnishNews', 'atctListAlbum_XXX',    'createLinguaLinks', 'findTypeBug', 'create_member_states',    'parlamentquestionscheck', 'deactivateWordCleanerForBelgium',    'create_seminar_test_data', 'rss_template', 'lingualink_view',    'addIATBlobFileInterfaces', 'faq_centralisation_helper',    'getFilePath', 'getBlobFilePath', 'checkMarkAsNews', 'checkpubs',    'migrateOshaAdaptation', 'setOshaMetadataExtension',    'translateBlog', 'setLinkListExtension', 'sq', 'bs', 'is', 'sr',    'mk', 'P1060730Berlinmeetingroom.jpg',    'P1060809Berlinicesmall10.jpg', 'portal_captchas',    'portal_catalog', 'setRemoteLanguageByLanguage',    'portal_catalog_real', 'getPortalCatalogInfoOnContext',    'publishAllFopsCillian', 'sh', 'get_aggregators',    'get_faq_tagging_info', 'synchronise_faq_tags', 'genlocalnav',    'renameFocalPointsCillian', 'minifyHTML', 'monthnames',    'len_month', 'calboxes', 'intelligent_breaker',    'recursiveReindexFOPs', 'listFOPlinksCillian',    'addMainFopPortletCillian', 'LCUpdateWSRegistrations',    'checkcontent', 'fixFOPNewsEventsPortletsCillian',    'hw2010_resources_promotionalmaterials_html', 'generateFlashText',    'DLF', 'hw2010_maintenance_accidents_html',    'hw2010_resources_campaignessentials_html',    'hw2010_resources_aboutsf_html_OLD', 'sitemap_3.xml.gz',    'hw2010_press_press_template', 'hw2010_events_template_html',    'getEventsDict', 'hw2010_news_template_html',    'hw2010_resources_fetchpublications', 'listAllCampaignSiteFiles',    'hw2010_resources_campaignessentials_html_tester',    'BatmosphereAudioEmbed.js', 'testPlayAudio', 'testlaunch.mp3',    'fire-and-explosion-risks-2013-protective-measures',    'hw2010_resources_promotionalmaterials_additional_languages',    'hw2010_press_multimedia_html',    'fire-and-explosion-risks-2013-protective-measures-el',    'incremental_reindex', 'inclog', 'subscribe_mailinglists',    'test_empty_focal_points', 'subtypeAllFopsCillian',    'analyse_subtyping', 'site_alive', 'hw2010_image_folders',    'hw2010_news_template_html_debug', 'hw2010_getPartnerById',    'hw2010_getPartnerFieldnames', 'hw2010_getPartners',    'hw2010_partners_old', 'parsePartners', 'hw2010_parsePartners',    'hw2010_partners.css', 'hw2010_partners_data',    'press-photos-banners-een-overview', 'propagateLinkList',    'exportXliff-Cillian', 'fonts', 'caching_policy_manager',    'HTTPCache', 'hw2010_press_multimedia_TEST', 'swfobject.js',    'CheckForStaleEntryInPC', 'hw2010_partner_detail',    'hw2010_partners', 'hw2010_get_presscontacts',    'addlocationstopasteventsfoldersinhw2010',    'hw2010_partner_detail_cornelis', 'hw2010_press_template',    'hw2010_eu_partners_listing', 'y_key_79ecfaf870f65216.html',    'langtest', 'hw2010_resources_aboutsf_html', 'portal_linkchecker',    'hw2010_fop_detail', 'hw2010_eu_fops_listing', 'outdated_info',    'base2-dom-fp.js', 'get_seminar_subcategories', 'me',    'logo-hw.png', 'contact_us_feedback', 'contact_us_method',    'expandable_content.js', 'retrieveAllPaths', 'LCRetrieveURLs',    'pressrelease_view', 'copy_of_hw2010_resources_fetchpublications',    'jwplayer.js', 'player.swf', 'genlocalnavhw2012',    'languagetesting', 'hw2012_get_languages', 'send_greeting_card',    'gatag.js', 'jquery.countdown.min.js',    'hw2012_resources_about_html',    'hw2012_resources_fetchpublications',    'hw2012_resources_campaignessentials_html',    'hw2012_resources_promotionalmaterials_html',    'hw2012_press_press_template', 'hw2012_get_presscontacts',    'hw2012_image_folders', 'linkcollection.js']

# Before
# $ ls -l var/filestorage/Data.fs
# -rw-r--r-- 1 oshawebdev service 31400491144 Apr 23 16:44 var/filestorage/Data.fs
# $ du -s var/blobstorage/
# 21264040        var/blobstorage/


count = 0

class ZopeFindImageWalker(Walker):
    def __init__(
        self, portal, migrator, **kwargs):
        self.portal = portal
        self.migrator = migrator
        self.src_portal_type = 'Image'
        self.src_meta_type = 'ATImage'
        self.dst_portal_type = 'Image'
        self.dst_meta_type = 'ATBlob'

        self.transaction_size = int(kwargs.get('transaction_size', 20))
        self.full_transaction = kwargs.get('full_transaction', False)
        self.use_savepoint = kwargs.get('use_savepoint', False)

        if self.full_transaction and self.use_savepoint:
            raise ValueError

        self.out = StringIO()
        self.counter = 0
        self.errors = []


    def go(self, **kwargs):
        """runner

        Call it to start the migration
        """
        self.migrate(self.walk(), **kwargs)

    def walk(self):
        top_node = self.portal.unrestrictedTraverse(
            "/osha/portal")

        for item in self._walk(top_node):
            if item is not None:
                yield itemh

    def _walk(self, node):
        global count
        if node.meta_type in ["Script (Python)", "External Method"]:
            return None
        for id, ob in node.ZopeFind(node, search_sub=0):
            if ob.meta_type == "ATImage":
                count += 1
                if count % 100 == 0:
                    print "Committing %s" %count
                    transaction.commit()
                print "%s %s" %(count, ob.absolute_url(1))
                if ob.getImage() is "":
                    print "Deleting %s" %ob.absolute_url(1)
                    parent = ob.aq_explicit.aq_parent
                    parent.manage_delObjects(ob.getId())
                else:
                    return ob
            else:
                # print "%s" %ob.absolute_url(1)
                self._walk(ob)
        return []


class MigrateImagesView(BrowserView):

    def __call__(self):
        portal = getSite()
        import pdb; pdb.set_trace()

        start_time = datetime.now()

        walker = ZopeFindImageWalker(
            portal, migrator=ATImageToBlobImageMigrator)
        walker.go()
        transaction.commit()
        # my_migrateATBlobImages(portal)
        # for obj_id in root_ids[:100]:
        #     print "Migrating %s" %obj_id
        #     migrateATBlobImages(portal[obj_id])

        print "Finished after %s seconds" %(datetime.now() - start_time)

