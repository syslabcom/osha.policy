"""
External method to help fix up incorrect subtype settings #1343
"""

from zope import component
from zope.component import getUtility
from zope.interface import providedBy

from Products.CMFCore.utils import getToolByName

from p4a.subtyper import interfaces
from p4a.subtyper.interfaces import ISubtyper

from slc.subsite.interfaces import ISubsiteEnhanced

# Given a list path/subtype tuples set the path obj to subtype
subtype_map = [
    ("/OSHA/en/oshnetwork/focal-points/germany", "None"),
    ("/OSHA/mt/oshnetwork/member-states/bulgaria-mt-mt", "slc.subsite.FolderSubsite"),
    ]

subtype_map = []

def run(self):
    raise Exception("Customize this script before running")
    def log(message):
        self.REQUEST.response.write(str(message)+"\n")

    def get_translation_obs(ob):
        return [i[0] for i in ob.getTranslations().values()]

    subtyper = component.getUtility(ISubtyper)

    def set_subtype(path, correct_subtype):
        """
        Set the subtype of the object at path and all of its translations to
        correct_subtype
        """
        obj = self.unrestrictedTraverse(path)
        for translation in get_translation_obs(obj):
            actual_subtype = subtyper.existing_type(translation)
            if correct_subtype == "None":
                if actual_subtype:
                    subtyper.remove_type(translation)
                    log("%s : removed subtype: %s"\
                        %(translation.absolute_url(), actual_subtype))
                else:
                    log("%s : not changed, subtype is None"\
                        %translation.absolute_url())
            elif actual_subtype and actual_subtype.name == correct_subtype:
                log("%s : already has the subtype: %s"\
                    %(translation.absolute_url(), actual_subtype.name))
            elif actual_subtype != correct_subtype:
                subtyper.change_type(translation, correct_subtype)
                log("%s : changed to subtype: %s"\
                    %(translation.absolute_url(), correct_subtype))


    for mapping in subtype_map:
        set_subtype(*mapping)

    # Set the subtype for all FOP folders to Subsite:

    # portal = self.portal_url.getPortalObject()
    # fop_root = portal.en.oshnetwork["focal-points"]
    # countries = [i for i in fop_root.objectIds() if fop_root[i].portal_type == "Folder"]
    # for country in countries:
    #     fop = fop_root[country].getPhysicalPath()
    #     set_subtype(fop, "slc.subsite.FolderSubsite")
