from Missing import MV
from Products.Five.browser import BrowserView
from collective.solr.flare import PloneFlare
from collective.solr.interfaces import ISearch

from collective.solr.utils import padResults
from DateTime import DateTime

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

        # Apply correct sorting
        key = None
        reverse = False
        if 'sort_on' in query:
            reverse = query.get('sort_order', '') in ['reverse', 'descending']
            key = query['sort_on']
        search_results = pc.searchResults(
            query, sort_index=key, reverse=reverse)

        # Find the originals of the preferred language translations:
        translation_uids = [
            x.UID for x in search_results if x.Language not in ['en', '']]
        originals = rc.search(
            {"relationship": "translationOf", "sourceUID": translation_uids})
        original_uids = [x.targetUID for x in originals]

        # Return all results except originals, leaving preferred
        # language translations and untranslated documents:
        results = [x for x in search_results if x.UID not in original_uids]

        return results

    def search_solr(self, query, **parameters):
        lang_tool = api.portal.get_tool("portal_languages")
        search = queryUtility(ISearch)
        if search is None:
            log.warn('Could not get solr ISearch utility')
            return []
        rc = api.portal.get_tool("reference_catalog")

        preferred_lang = lang_tool.getPreferredLanguage()
        languages = ["en", "any"]


        # Speed approach
        # * Search for all en and neutral items with a given batch size
        # * If current language is en: return
        # * Take the found items and feed their UIDs into the reference catalog
        # * Look up any items that are translations of these in the current
        #    language
        # * Replace the items with their translations
        # * Pad the result
        # * Return result
        query = ' '.join((
            query, "+Language:({0})".format(' OR '.join(languages))))
        i = 0
        i+=1;log.warn('Step %s at %s' % (i, DateTime()))

        if 'rows' not in parameters:
            parameters['rows'] = 100000
        if 'start' not in parameters:
            parameters['start'] = 0

        solr_response = search(query, **parameters)
        i+=1;log.warn('Step %s at %s' % (i, DateTime()))

        if not solr_response:
            return solr_response

        results = solr_response.results()
        schema = search.getManager().getSchema() or {}


        #found_results = results[parameters[start]:parameters[start]+parameters[rows]]
        original_uids = [x.UID for x in results]

        translations = rc.search({
            "relationship": "translationOf",
            "targetUID": original_uids,
        })
        i+=1;log.warn('Step %s at %s' % (i, DateTime()))
        target_map = {}       # maps canonicals to translations
        source_map = {}       # maps translations to canonicals
        translation_map = {}  # used to store translations under the uid of the canonical
        # create a map where every translation is stored under the UID of the canonical
        for t in translations:
            if t.Language != preferred_lang:
                continue
            target_map[t['targetUID']] = t['sourceUID']
            source_map[t['sourceUID']] = t['targetUID']

        # search for the full brains of the translations
        i+=1;log.warn('Step %s at %s' % (i, DateTime()))
        if target_map:
            t_query = "Language:%s AND UID: (%s)" % (preferred_lang, ' OR '.join(target_map.values()))
            translation_response = search(t_query)
            for item in translation_response:
                targetUID = source_map[item.UID]
                if item.Language == preferred_lang:
                    translation_map[targetUID] = item


        i+=1;log.warn('Step %s at %s' % (i, DateTime()))
        for idx, flare in enumerate(results):
            if flare.UID not in translation_map.keys():
                flare = PloneFlare(flare)
            else:
                flare = PloneFlare(translation_map[flare.UID])

            for missing in set(schema.stored).difference(flare):
                flare[missing] = MV
            results[idx] = flare

        i+=1;log.warn('Step %s at %s' % (i, DateTime()))
        padResults(results, **parameters)
        i+=1;log.warn('Step %s at %s' % (i, DateTime()))

        return solr_response

