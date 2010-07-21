from copy import copy
from StringIO import StringIO

import Acquisition
import transaction

from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFCore.utils import getToolByName
from zope.component.interfaces import ComponentLookupError
from osha.fop.portlets import fop_main_promotion
from plone.app.portlets.browser.editmanager import ManagePortletAssignments
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from plone.app.portlets.utils import assignment_mapping_from_key
from zope.exceptions.interfaces import DuplicationError

from osha.theme.browser.viewlets import OSHANetworkchooser


#networks = OSHANetworkchooser(self, self.REQUEST, None, None).networks()

fop_main_sites = {
    'belgium': 'be.osha.europa.eu',
    'bulgaria': 'bg.osha.europa.eu',
    'cyprus': 'cy.osha.europa.eu',
    'czech-republic': 'cz.osha.europa.eu',
    'estonia': 'ee.osha.europa.eu',
    'finland': 'fi.osha.europa.eu',
    'france': 'fr.osha.europa.eu',
    'germany': 'de.osha.europa.eu',
    'greece': 'gr.osha.europa.eu',
    'hungary': 'hu.osha.europa.eu',
    'italy': 'it.osha.europa.eu',
    'latvia': 'lv.osha.europa.eu',
    'netherlands': 'nl.osha.europa.eu',
    'norway': 'no.osha.europa.eu',
    'romania': 'ro.osha.europa.eu',
    'slovakia': 'sk.osha.europa.eu',
    'slovenia': 'si.osha.europa.eu',
    'spain': 'es.osha.europa.eu',
    'sweden': 'se.osha.europa.eu',
    'switzerland': 'ch.osha.europa.eu',
}

{
#dropped
    'denmark': 'dk.osha.europa.eu',
    'poland': 'pl.osha.europa.eu',

#not mentioned
    'austria': 'at.osha.europa.eu',
    'iceland': 'www.vinnueftirlit.is',
    'ireland': 'ie.osha.europa.eu',
    'lithuania': 'osha.vdi.lt',
    'luxembourg': 'lu.osha.europa.eu',
    'malta': 'mt.osha.europa.eu',
    'portugal': 'pt.osha.europa.eu',
    'turkey': 'tr.osha.europa.eu',
    'united-kingdom': 'uk.osha.europa.eu',
    }

fop_group_map = {
 "albania" : "fop_albania",
 "austria" : "fop_austria",
 "belgium" : "fop_belgium_editors",
 "bosnia-and-herzegovina" : "fop_bosnia_and_herzegovina",
 "bulgaria" : "fop_bulgaria",
 "croatia" : "fop_croatia",
 "cyprus" : "fop_cyprus",
 "czech-republic" : "fop_czech_republic",
 "denmark" : "fop_denmark",
 "estonia" : "fop_estonia",
 "finland" : "fop_finland",
 "france" : "fop_france",
 "germany" : "fop_germany",
 "greece" : "fop_greece",
 "hungary" : "fop_hungary",
 "iceland" : "fop_iceland",
 "ireland" : "fop_ireland",
 "italy" : "fop_italy",
 "kosovo-under-unscr-1244-99" : "fop_kosovo_under_unscr_1244_99",
 "latvia" : "fop_latvia",
 "liechtenstein" : "fop_liechtenstein",
 "lithuania" : "fop_lithuania",
 "luxembourg" : "fop_luxemburg",
 "malta" : "fop_malta",
 "montenegro" : "fop_montenegro",
 "netherlands" : "fop_netherlands",
 "norway" : "fop_norway",
 "poland" : "fop_poland",
 "portugal" : "fop_portugal",
 "romania" : "fop_romania",
 "serbia" : "fop_serbia",
 "slovakia" : "fop_slovakia",
 "slovenia" : "fop_slovenia",
 "spain" : "fop_spain",
 "sweden" : "fop_sweden",
 "switzerland" : "fop_switzerland",
 "the-former-yugoslav-republic-of-macedonia" : "fop_the_former_yugoslav_republic_of_macedonia",
 "turkey" : "fop_turkey",
 "united-kingdom" : "fop_united_kingdom",
}


def main(self):
    raise Exception("This script must be customised before running")
    # Assing the FOP main site portlet to each FOP section
    # 1) Remove any FOP main site portlets already assigned
    # 2) Assign a new one in the desired position
    # 3) If there is a url already defined for it add this to the EN portlet
    portal = self.portal_url.getPortalObject()

    def log(message):
        self.REQUEST.response.write(str(message)+"\n")

    def get_translation_obs(ob):
        return [i[0] for i in ob.getTranslations().values()]

    # copied from plone.app.portlets
    def move_portlet_up(assignments, name):
        keys = list(assignments.keys())
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)

    def set_path_criterion_to_uid(ob, target_uid):
        try:
            location_criterion = ob.getCriterion(
                "crit__path_ATPathCriterion"
                )
        except AttributeError:
            location_criterion = ob.addCriterion(
                field="path",criterion_type="ATPathCriterion"
                )
        location_criterion.setValue([target_uid])
        location_criterion.setRecurse(True)
        #location_criterion._setUID(target_uid)

    def set_language_criterion_to_lang(ob, lang):
        try:
            language_criterion = ob.getCriterion(
                'crit__Language_ATSelectionCriterion'
                )
        except AttributeError:
            language_criterion = ob.addCriterion(
                field="Language",
                criterion_type='ATSelectionCriterion'
                )
        language_criterion.setValue([lang])
        log("Set language criterion")

    def add_remove_portlets(country, obj):
        """
        Add/Configure/Position the FOP main site portlet
        Remove the "activities" portlet if present
        """
        path = '/'.join(obj.getPhysicalPath())
        try:
            right = assignment_mapping_from_key(obj, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
        except ComponentLookupError:
            log("no portlets possible for %s" %obj)
            return
        portlets = [x for x in list(right.keys())]
        if "fop-main-site" in portlets:
            log("Removing existing FOP main site portlet")
            del right["fop-main-site"]
        if "activities" in portlets:
            log("Removing existing activities portlet")
            del right["activities"]

        fop_url = ""
        # The url only needs to be defined on the canonical translation
        if obj.Language() == "en" and country in fop_main_sites.keys():
            # Add the main FOP url url to the portlet
            fop_url = "http://"+fop_main_sites[country]
            log("Set url to %s" %fop_url)

        right["fop-main-site"] = fop_main_promotion.Assignment(url=fop_url)
        log("Added main FOP portlet")

        fop_position = 0
        portlets = [x for x in list(right.keys())]
        index = portlets.index('fop-main-site')
        while index > fop_position:
            log("Moving the portlet to the correct position")
            move_portlet_up(right, "fop-main-site")
            index = list(right.keys()).index("fop-main-site")



    def configure_news_and_events(country, translation):
        """
        FOPs which have a Main Site should display news and events
        from the main site.
        """
        if country in fop_main_sites.keys():
            """point the news and events at the main site"""
            main_fop = portal.fop[country]
            default_lang = main_fop.portal_languages.getDefaultLanguage()
            main_fop_lang = main_fop[default_lang]
            pt = getToolByName(portal, 'portal_types')
            folder_type = pt.getTypeInfo("Folder")
            # Deliberately bypassing the security mechanism so that
            # Anonymous users can also create this folder
            if not hasattr(main_fop_lang, "news"):
                # Some FOPs don't allow folders to be created so we're
                # bypassing security checks
                # main_fop_lang.invokeFactory(type_name="Folder", id="news")
                factory_method = folder_type._getFactoryMethod(
                    main_fop_lang, check_security=0
                    )
                factory_method("news")
                log("Created News folder")
            main_news = main_fop_lang.news
            set_path_criterion_to_uid(
                translation.news["front-page"], main_news.UID()
                )
            if not hasattr(main_fop_lang, "events"):
                factory_method = folder_type._getFactoryMethod(
                    main_fop_lang, check_security=0
                    )
                factory_method("events")
                log("Created Events folder")
            main_events = main_fop_lang.events
            set_path_criterion_to_uid(
                translation.events["front-page"], main_events.UID()
                )
            set_language_criterion_to_lang(
                translation.news["front-page"], default_lang
                )
            set_language_criterion_to_lang(
                translation.events["front-page"], default_lang
                )
            log("Set news and events to show results from the main site")

    fop_root = portal.en.oshnetwork["focal-points"]
    countries = fop_root.listFolderContents(contentFilter={"portal_type":"Folder"})
    log(countries)
    #countries = [fop_root.austria]
    for fop in countries:
        country = fop.getId()
        group = fop_group_map[country]
        for translation in get_translation_obs(fop):
            log("Setting local role on %s"%translation.absolute_url())
            translation.manage_setLocalRoles(group, ["Contributor", "Editor", "Member", "Reviewer"])
            # add_remove_portlets(country, translation)
            # configure_news_and_events(country, translation)
            # set_path_criterion_to_uid(translation, portal.en.news.UID())
        transaction.commit()
