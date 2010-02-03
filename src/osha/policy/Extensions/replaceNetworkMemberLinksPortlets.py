"""
Run the script from "en" member-states folder

get the index_html for each country, replace it's portlet, get all
it's translations and do the same

"""

from StringIO import StringIO

from zope.component.interfaces import ComponentLookupError

from Products.LinguaPlone.interfaces import ITranslatable
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY

from osha.fop.portlets import fop_links


def replace_nm_links_portlets(self):
    """
    Recursively replace 'network-member-links' portlets with the
    new 'fop-links' portlet
    """
    self.out = StringIO()
    self.out.write(
        'Replacing network-member-links portlets with fop-portlets.\n\n'
        )

    def move_portlet_up(assignments, name):
        """
        copied from plone.app.portlets
        """
        keys = list(assignments.keys())
        idx = keys.index(name)
        keys.remove(name)
        keys.insert(idx-1, name)
        assignments.updateOrder(keys)

    def do_portlet_replacement(obj):
        """
        Replace a "network-member-links" portlets with a "fop-links" portlet
        """
        path = '/'.join(obj.getPhysicalPath())
        try:
            right = assignment_mapping_from_key(
                obj, 'plone.rightcolumn', CONTEXT_CATEGORY, path
                )
        except ComponentLookupError:
            return

        portlets = [x for x in list(right.keys())]
        old_portlet = "network-member-links"
        new_portlet = 'fop-links'
        if old_portlet in portlets:
            index = portlets.index(old_portlet)
            del right[old_portlet]
            if new_portlet in portlets:
                return
            right[new_portlet] = fop_links.Assignment()

            keys =  list(right.keys())
            new_portlet_index = keys.index(new_portlet)
            while new_portlet_index > index:
                move_portlet_up(right, new_portlet)
                keys =  list(right.keys())
                new_portlet_index = keys.index(new_portlet)
            print [x for x in list(right.keys())]
            self.out.write('Portlet replacement on %s successful\n' %path)

    portal = self.portal_url.getPortalObject()
    member_states = portal.en.oshnetwork["member-states"].listFolderContents(
        contentFilter={"portal_type": "Folder"}
        )
    for member_state in member_states:
        index_page = getattr(member_state, "index_html", None)
        if index_page:
            translatable = ITranslatable(index_page, None)
            if translatable is not None:
                translations = translatable.getTranslations()
            else:
                translations = {}

            for lang_code in translations:
                translation = translations[lang_code][0]
                do_portlet_replacement(translation)

    return self.out.getvalue()
