from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api


class LanguageFallbackSearch(BrowserView):
    """OSHA requires that searches return translations in the
    preferred language where possible, and otherwise return
    English/Lanuage neutral items."""

    def search(self, query):
        """
        """
        
        lang_tool = api.portal.get_tool("portal_languages")
        pc = api.portal.get_tool("portal_catalog")
        rc = api.portal.get_tool("reference_catalog")

        # Search for both canonical, langauge-neutral and preferred language translations.
        preferred_lang = lang_tool.getPreferredLanguage()
        languages = ["en", ""]
        if preferred_lang not in languages:
            languages.append(preferred_lang)
        query["Language"] = languages
        search_results = pc.search(query)

        # Find the originals of the preferred language translations:
        translation_uids = [x.UID for x in search_results if x.Language not in ['en', '']]
        originals = rc.search({"relationship":"translationOf", "sourceUID": translation_uids})
        original_uids = [x.targetUID for x in originals]

        # Return all results except originals, leaving preferred language translations
        # and untranslated documents:
        return [x for x in search_results if x.UID not in original_uids]
        
        
