from Missing import MV
from Products.Five.browser import BrowserView
from collective.solr.flare import PloneFlare
from collective.solr.interfaces import ISearch

from plone import api
from zope.component import queryUtility

import logging

log = logging.getLogger(__name__)


class LanguageFallbackSearch(BrowserView):
    """OSHA requires that searches return translations in the
    preferred language where possible, and otherwise return
    English/Lanuage neutral items."""

    def _mangle_query(self, query):
        lang_tool = api.portal.get_tool("portal_languages")
        # Search for both canonical, langauge-neutral and preferred
        # language translations.
        preferred_lang = lang_tool.getPreferredLanguage()
        languages = ["en", ""]
        if preferred_lang not in languages:
            languages.append(preferred_lang)
        query["Language"] = languages
        if 'path' in query:
            portal = api.portal.get()
            # Find all language paths that correspond to the given path
            if isinstance(query['path'], dict):
                path = query['path']['query']
            else:
                path = query['path']
            if isinstance(path, (str, unicode)):
                path = [path]

            for p in path[:]:
                # api.content.get currently doesn't work when the portal is
                # in a subfolder.
                # Besides, it does basically the same thing, but looks up the
                # portal every time.
                ob = portal.restrictedTraverse(p)
                try:
                    canonical = ob.getCanonical()
                except AttributeError:
                    # Not translated or translateable:
                    continue
                cpath = '/'.join(canonical.getPhysicalPath())
                if cpath != p:  # Don't add it if it *is* the canonical.
                    path.append(cpath)

            # Add the new paths back:
            if isinstance(query['path'], dict):
                query['path']['query'] = path
            else:
                query['path'] = path
        return query

    def search(self, query):
        pc = api.portal.get_tool("portal_catalog")
        rc = api.portal.get_tool("reference_catalog")
        query = self._mangle_query(query)

        search_results = pc.search(query)

        # Find the originals of the preferred language translations:
        translation_uids = [
            x.UID for x in search_results if x.Language not in ['en', '']]
        originals = rc.search(
            {"relationship": "translationOf", "sourceUID": translation_uids})
        original_uids = [x.targetUID for x in originals]

        # Return all results except originals, leaving preferred
        # language translations and untranslated documents:
        results = [x for x in search_results if x.UID not in original_uids]

        # Apply correct sorting
        if 'sort_on' in query:
            reverse = query.get('sort_order', '') == 'reverse'
            key = query['sort_on']
            results = sorted(
                results, key=lambda x: getattr(x, key), reverse=reverse)

        return results

    def search_solr(self, query, **parameters):
        lang_tool = api.portal.get_tool("portal_languages")
        search = queryUtility(ISearch)
        if search is None:
            log.warn('Could not get solr ISearch utility')
            return []
        rc = api.portal.get_tool("reference_catalog")

        # Search for both canonical, language-neutral and preferred lang
        # translations.
        # XXX MISSING? Mangling the path?
        preferred_lang = lang_tool.getPreferredLanguage()
        languages = ["en", "any"]
        if preferred_lang not in languages:
            languages.append(preferred_lang)
        query = ' '.join((
            query, "+Language:({0})".format(' OR '.join(languages))))
        parameters['rows'] = 100000
        start = parameters.get('start', 0)
        parameters['start'] = 0
        search_results = search(query, **parameters)

        # Find the originals of the preferred language translations:
        translation_uids = [
            x.UID for x in search_results if x.Language not in ['en', '']]
        originals = rc.search({
            "relationship": "translationOf",
            "sourceUID": translation_uids,
        })
        original_uids = [x.targetUID for x in originals]

        results = search_results.results()
        schema = search.getManager().getSchema() or {}
        for idx, flare in enumerate(results[:]):
            if flare.UID not in original_uids:
                flare = PloneFlare(flare)
                for missing in set(schema.stored).difference(flare):
                    flare[missing] = MV
                results[idx] = flare
        # Return all results except originals, leaving preferred
        # language translations and untranslated documents:
        filtered_results = [
            x for x in search_results
            if x.UID not in original_uids
        ]
        if start:
            results[0:0] = [None] * start
        found = int(len(filtered_results))
        tail = found - len(results)
        filtered_results.extend([None] * tail)
        return filtered_results
