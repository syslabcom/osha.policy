"""
Extra migration steps which are not carried out by the Plone 4
migration
"""

import transaction

portal = app.osha.portal

reindex_count = 0

def find_and_reindex(context, sub=False):
    global reindex_count
    for id, elem in context.ZopeFind(context, search_sub=sub):
        if elem.meta_type == "Script (Python)":
            continue
        if hasattr(elem.aq_explicit, "portal_type"):
            reindex_count += 1
            elem.reindexObject()
            print "%s %s %s" %(
                reindex_count, elem.portal_type, elem.absolute_url(1))
            if reindex_count % 500 == 0:
                print "Committing"
                transaction.commit()

def reindex_path(path, include_translations=False, sub=False):
    context = app.osha.portal.unrestrictedTraverse(path)
    print "Reindexing %s, %sincluding translations" %(
        context.absolute_url(1), not include_translations and "not " or "")
    if include_translations:
        for translation in context.getTranslations().values():
            find_and_reindex(translation[0], sub)
    else:
        find_and_reindex(context)

## Upgrade the FAQ section, This requires that
from Products.PloneHelpCenter.upgrades import (
    migrateNextPrev, migrateBodyTexts, migrateFAQs)

def migrate_faqs():
    reindex_path(
        "/osha/portal/en/faq", include_translations=True, sub=True)
    transaction.commit()

    migrateNextPrev(portal)
    migrateBodyTexts(portal)
    migrateFAQs(portal)
    transaction.commit()

if __name__ == "__main__":
    migrate_faqs()
