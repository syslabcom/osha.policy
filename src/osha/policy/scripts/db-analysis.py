from types import *
from datetime import datetime


root_ids =     [    'portal_setup', 'MailHost', 'content_type_registry', 'error_log',    'plone_utils', 'portal_actionicons', 'portal_actions',    'portal_atct', 'portal_controlpanel', 'portal_css', 'portal_diff',    'portal_discussion', 'portal_factory', 'portal_groupdata',    'portal_groups', 'portal_interface', 'portal_javascripts',    'portal_kss', 'portal_memberdata', 'portal_membership',    'portal_metadata', 'portal_migration', 'portal_password_reset',    'portal_properties', 'portal_quickinstaller',    'portal_registration', 'portal_skins', 'portal_syndication',    'portal_types', 'portal_uidannotation', 'portal_uidgenerator',    'portal_undo', 'portal_url', 'portal_view_customizations',    'portal_workflow', 'translation_service',    'portal_form_controller', 'mimetypes_registry',    'portal_transforms', 'archetype_tool', 'reference_catalog',    'uid_catalog', 'acl_users', 'kupu_library_tool',    'portal_archivist', 'portal_historiesstorage',    'portal_historyidhandler', 'portal_modifier',    'portal_purgepolicy', 'portal_referencefactories',    'portal_repository', 'portal_uidhandler', 'portal_languages',    'RAMCache_RAM', 'ResourceRegistryCache', 'Members',    'portal_placeful_workflow', 'marshaller_registry',    'portal_countryutils', 'sin_tool', 'portal_vocabularies', 'data',    'en', 'bg', 'cs', 'da', 'nl', 'et', 'fi', 'fr', 'de', 'el', 'hu',    'it', 'lv', 'lt', 'mt', 'pl', 'pt', 'ro', 'sk', 'sl', 'es', 'sv',    'ReindexHelper', 'images', 'reindexThis', 'tr', 'no', 'ownertest',    'ReindexHelperPath', 'new-case-study', 'perftest',    '.wf_policy_config', 'portal_calendar', 'tmp',    'portal_alertservice', 'portal_ploneboard', 'hr',    'google_test_cse3', 'index_html', 'eopro', 'directory',    'CacheSetup_ResourceRegistryCache_RAM', 'portal_redirection',    'sql', 'subscriptions.js', 'scripts', 'logo_small.gif',    'google9f3b856e9891b67d.html', 'googleef20cdffcecd6736.html',    'google532cc25ad07b2121.html', 'persistSiteMap',    'googlec8582979cf35e207.html', 'default_error_message',    'checkUnmigratedNace', 'checklist_hotels_data',    'sitemap_1.xml.gz', 'sitemap_index.xml.gz', 'osha',    'MemcachedManager', 'RAMCache', 'lists-database',    'napofilmstructure', 'getRID', 'sub', 'airliquide.jpg',    'baxter.jpg', 'copy_of_baxter.jpg', 'cesi.jpg', 'efnms.jpg',    'epsc.jpg', 'ge.jpg', 'imaginationatwork.jpg', 'lilly.jpg',    'ima.jpg', 'copy_of_efnms.jpg', 'reporting', 'LCRetrieveByDate',    'fop', 'sitemap_2.xml.gz', 'SCRIPTS', 'cleanNewOshEraCat',    'fixImportTags', 'uniqueValuesForSubject', 'cleanWordPastedText',    'LCRetrieveByPath', 'lcregisterThis', 'topbannerwos.jpg',    'google', 'portal_cache_settings', 'portal_squid', 'formgen_tool',    'relations_library', 'getUID', 'set_uploaded_file_titles.bak',    'resource_centralisation_helper', 'exchangeSEPPortlets',    'checkMemberFoldersForOSHLinks', 'testpubbysubject', 'test',    'test_em', 'checkFinnishNews', 'atctListAlbum_XXX',    'createLinguaLinks', 'findTypeBug', 'create_member_states',    'parlamentquestionscheck', 'deactivateWordCleanerForBelgium',    'create_seminar_test_data', 'rss_template', 'lingualink_view',    'addIATBlobFileInterfaces', 'faq_centralisation_helper',    'getFilePath', 'getBlobFilePath', 'checkMarkAsNews', 'checkpubs',    'migrateOshaAdaptation', 'setOshaMetadataExtension',    'translateBlog', 'setLinkListExtension', 'sq', 'bs', 'is', 'sr',    'mk', 'P1060730Berlinmeetingroom.jpg',    'P1060809Berlinicesmall10.jpg', 'portal_captchas',    'portal_catalog', 'setRemoteLanguageByLanguage',    'portal_catalog_real', 'getPortalCatalogInfoOnContext',    'publishAllFopsCillian', 'sh', 'get_aggregators',    'get_faq_tagging_info', 'synchronise_faq_tags', 'genlocalnav',    'renameFocalPointsCillian', 'minifyHTML', 'monthnames',    'len_month', 'calboxes', 'intelligent_breaker',    'recursiveReindexFOPs', 'listFOPlinksCillian',    'addMainFopPortletCillian', 'LCUpdateWSRegistrations',    'checkcontent', 'fixFOPNewsEventsPortletsCillian',    'hw2010_resources_promotionalmaterials_html', 'generateFlashText',    'DLF', 'hw2010_maintenance_accidents_html',    'hw2010_resources_campaignessentials_html',    'hw2010_resources_aboutsf_html_OLD', 'sitemap_3.xml.gz',    'hw2010_press_press_template', 'hw2010_events_template_html',    'getEventsDict', 'hw2010_news_template_html',    'hw2010_resources_fetchpublications', 'listAllCampaignSiteFiles',    'hw2010_resources_campaignessentials_html_tester',    'BatmosphereAudioEmbed.js', 'testPlayAudio', 'testlaunch.mp3',    'fire-and-explosion-risks-2013-protective-measures',    'hw2010_resources_promotionalmaterials_additional_languages',    'hw2010_press_multimedia_html',    'fire-and-explosion-risks-2013-protective-measures-el',    'incremental_reindex', 'inclog', 'subscribe_mailinglists',    'test_empty_focal_points', 'subtypeAllFopsCillian',    'analyse_subtyping', 'site_alive', 'hw2010_image_folders',    'hw2010_news_template_html_debug', 'hw2010_getPartnerById',    'hw2010_getPartnerFieldnames', 'hw2010_getPartners',    'hw2010_partners_old', 'parsePartners', 'hw2010_parsePartners',    'hw2010_partners.css', 'hw2010_partners_data',    'press-photos-banners-een-overview', 'propagateLinkList',    'exportXliff-Cillian', 'fonts', 'caching_policy_manager',    'HTTPCache', 'hw2010_press_multimedia_TEST', 'swfobject.js',    'CheckForStaleEntryInPC', 'hw2010_partner_detail',    'hw2010_partners', 'hw2010_get_presscontacts',    'addlocationstopasteventsfoldersinhw2010',    'hw2010_partner_detail_cornelis', 'hw2010_press_template',    'hw2010_eu_partners_listing', 'y_key_79ecfaf870f65216.html',    'langtest', 'hw2010_resources_aboutsf_html', 'portal_linkchecker',    'hw2010_fop_detail', 'hw2010_eu_fops_listing', 'outdated_info',    'base2-dom-fp.js', 'get_seminar_subcategories', 'me',    'logo-hw.png', 'contact_us_feedback', 'contact_us_method',    'expandable_content.js', 'retrieveAllPaths', 'LCRetrieveURLs',    'pressrelease_view', 'copy_of_hw2010_resources_fetchpublications',    'jwplayer.js', 'player.swf', 'genlocalnavhw2012',    'languagetesting', 'hw2012_get_languages', 'send_greeting_card',    'gatag.js', 'jquery.countdown.min.js',    'hw2012_resources_about_html',    'hw2012_resources_fetchpublications',    'hw2012_resources_campaignessentials_html',    'hw2012_resources_promotionalmaterials_html',    'hw2012_press_press_template', 'hw2012_get_presscontacts',    'hw2012_image_folders', 'linkcollection.js']


def find_obs(context):
    if context.meta_type in ["Script (Python)", "External Method"]:
        return 0

    total_dir_size = 0
    global  file_info, dir_info, start_time, du

    for id, ob in context.ZopeFind(context ,search_sub=0):
        size = getattr(ob, "get_size", None)
        if size is not None:
            size = size()
        else:
            size = 0

        modified = getattr(ob, "modified", None)
        if modified is not None:
            modified = modified()
        else:
            modified = "1970/1/1"

        file_info.write("'%s', '%s', '%s', '%s', '%s'\n" %(
                size, id, ob.absolute_url(1), ob.meta_type, modified))

        if hasattr(ob.aq_explicit, "objectIds"):
            if len(ob.objectIds()) > 0:
                size = find_obs(ob)

        total_dir_size += size

    dir_info.write("'%s', '%s', '%s', '%s', '%s'\n" %(
                total_dir_size, context.getId(),
                context.absolute_url(1), context.meta_type,
                context.modified()))
    return total_dir_size


def main():
    global  file_info, dir_info, start_time, du


    portal = app.osha.portal

    start_time = datetime.now()
    file_info = open("db-files-2.csv", "w")
    dir_info = open("db-dirs-2.csv", "w")

    print "Starting"

    for obj_id in root_ids[100:]:
        print "%s %s" %(find_obs(portal[obj_id]), obj_id)
    # find_obs(portal["de"]["conferences-de"]["eemhof_2006-de"])
    # find_obs(portal["de"])
    #find_obs(portal)

    file_info.close()
    dir_info.close()
    print "Finished after %s seconds" %(datetime.now() - start_time)

if __name__ == "__main__":
    main()
