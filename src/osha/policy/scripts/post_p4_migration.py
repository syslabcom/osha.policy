"""
Extra migration steps which are not carried out by the Plone 4
migration
"""

from Testing.makerequest import makerequest
import transaction

portal = app.osha.portal
uc = portal.uid_catalog

reindex_count = 0

def find_and_reindex(context, sub=False):
    global reindex_count
    for id, elem in context.ZopeFind(context, search_sub=sub):
        if elem.meta_type == "Script (Python)":
            continue
        if hasattr(elem.aq_explicit, "portal_type"):
            reindex_count += 1
            try:
                # reindexing Collage items requires a req
                makerequest(elem).reindexObject()
            except:
                print "getCanonical() fails for %s" %elem.absolute_url(1)
                #elem.reindexObject()
            #uc.catalogObject(elem, elem.absolute_url(1))
            print "%s %s %s" %(
                reindex_count, elem.portal_type, elem.absolute_url(1))
            if reindex_count % 100 == 0:
                print "Committing"
                try:
                    transaction.commit()
                except Exception, e:
                    import pdb; pdb.set_trace()

def reindex_path(path, include_translations=False, sub=False):
    context = app.osha.portal.unrestrictedTraverse(path)
    print "Reindexing %s, %sincluding translations" %(
        context.absolute_url(1), not include_translations and "not " or "")
    if include_translations:
        translations = context.getTranslations().values()
        for translation in translations:
            find_and_reindex(translation[0], sub)
    else:
        find_and_reindex(context, sub)

## Upgrade the FAQ section,
from Products.PloneHelpCenter.upgrades import (
    migrateNextPrev, migrateBodyTexts, migrateFAQs)

def fix_persistent_utils():
    """ Untested: should remove the registration of the
    osha.lingualinks portlet """
    sm = app.osha.portal.getSiteManager()
    ll = [i for i in sm._utility_registrations if i[1] == "osha.lingualinks"][0]
    del sm._utility_registrations[ll]
    transaction.commit()

def fix_section():
    # reindex_path(
    #     "/osha/portal/en/faq", include_translations=True, sub=True)
    # transaction.commit()

    migrateNextPrev(portal)
    migrateBodyTexts(portal)
    migrateFAQs(portal)
    transaction.commit()

#    languages = portal.portal_languages.getSupportedLanguages()
#    languages.remove("en")
#    for lang in languages:
#        reindex_path(
#            "/osha/portal/fop" ,
#            include_translations=False, sub=True)
#    transaction.commit()

if __name__ == "__main__":
    fix_section()
    # fix_persistent_utils()
