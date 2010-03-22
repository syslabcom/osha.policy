from copy import copy
from StringIO import StringIO

import Acquisition
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


def main(self):
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

    def set_path_criterion_to_uid(ob, uid):
        try:
            location_criterion = ob.getCriterion(
                "crit__path_ATPathCriterion"
                )
        except AttributeError:
            location_criterion = ob.addCriterion(
                field="path",criterion_type="ATPathCriterion"
                )
        location_criterion._setUID(target_uid)


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
            fop_url = fop_main_sites[country]
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
            main_news = main_fop.default_lang.news
            main_events = main_fop.default_lang.events
            set_path_criterion_to_uid(translation.news, main_news.UID())
            set_path_criterion_to_uid(translation.events, main_events.UID())
            log("Set news and events to show results from the main site")

    fop_root = portal.en.oshnetwork["member-states"]
    countries = fop_root.objectIds()
    for country in countries:
        fop = fop_root[country]
        fop_links = copy(fop.annotatedlinklist)
        for translation in get_translation_obs(fop):
            log(i.absolute_url())
            add_remove_portlets(country, translation)
            configure_news_and_events(country, translation)
            translation.annotatedlinklist = fop_links
