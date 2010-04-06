from zope import component
from zope.interface import providedBy
import transaction

from Products.CMFCore.utils import getToolByName
from osha.adaptation.subtyper import IAnnotatedLinkList 
from p4a.subtyper.interfaces import ISubtyper

def run(self):
    # This script must be customised before running
    raise Exception
    def log(message):
        self.REQUEST.response.write(str(message)+"\n")

    def get_translation_obs(ob):
        return [i[0] for i in ob.getTranslations().values()]

    subtyper = component.getUtility(ISubtyper)

    portal = self.portal_url.getPortalObject()
    fop_root = portal.en.oshnetwork["focal-points"]
    countries = [i for i in fop_root.objectIds() if fop_root[i].portal_type == "Folder"]

    countries = ['slovakia']
    for country in countries:
        fop = fop_root[country]
        doc = fop.get("index_html", None)
        if doc:
            # [log(i) for i in providedBy(doc)]
            # log(IAnnotatedLinkList.providedBy(doc))
            for translation in get_translation_obs(doc):
                type = subtyper.existing_type(doc)
                # log("%s : %s" %(translation.absolute_url(), type))
                if not IAnnotatedLinkList.providedBy(translation):
                    log("ERROR %s : %s" %(translation.absolute_url(), type))
                    subtyper.change_type(translation, 'annotatedlinks')
                    log("Updated %s" %translation.absolute_url())
                    transaction.commit()

                #if type and type.name == 'annotatedlinks':
                #    try:
                #        subtyper.remove_type(translation)
                #    except:
                #        pass
                #subtyper.change_type(translation, 'annotatedlinks')
                # log("Updated %s" %translation.absolute_url())
                # transaction.commit()
        else:
            log("ERROR index_html is missing %s" %fop.absolute_url())
