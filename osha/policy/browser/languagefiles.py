from zope.interface import implements
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
#from Products.CMFCore.interfaces._content import IFolderish

from osha.policy.browser.interfaces import ILanguageFiles

TYPES = ['ATBlob', 'ATFile', 'ATImage']

class LanguageFiles(BrowserView):
    implements(ILanguageFiles)


    def __call__(self):
        obj = self.context
        self.plt = getToolByName(obj, 'portal_languages')
        can = obj.getCanonical()
        default_lang = can.Language()
        obj_lang = obj.Language()
#        # if we're dealing with a translated folder, handle if first, the proceed to the canonical
#        if can != obj:
#            for item in obj.objectItems(TYPES):
#                lang, namestem, suffix = self._guessLanguage(item[0])
#                if item[1].Language()!= lang:
#                    item[1].setLanguage(lang)

        filenames = list()

        # We need a dict of dicts that maps filestems to a dicts of filenames by Language
        # { 'contract_notice_' : {
        #     'da' : 'contract_notice_da.pdf',
        #     'en' : 'contract_notice_en.pdf'
        #   }
        filesByLanguage = dict()

        items = [x for x in can.objectItems(TYPES)]
        for item in items:
            lang, namestem, suffix = self._guessLanguage(item[0])
            if not filesByLanguage.has_key(namestem):
                filesByLanguage[namestem] = dict()
            filesByLanguage[namestem][lang] = item[0]
            if item[1].Language()!= lang:
                item[1].setLanguage(lang)
                filenames.append(item[0])

        message = u'Set language according to suffix on these files:\n' +', '.join(filenames)
        message += u'Files were translation-linked according to filenames.'

        self.linkTranslations(filesByLanguage)

        path = obj.absolute_url()
        getToolByName(obj, 'plone_utils').addPortalMessage(message)
        self.request.RESPONSE.redirect(path)


    def linkTranslations(self, filesByLanguage):
        """ Link files as translations based on filenames """
        default_lang = self.plt.getDefaultLanguage()

        for filestem in filesByLanguage.keys():
            versions = filesByLanguage[filestem]
            # if no file version in the default language is available,
            # we have to randomly pick one language as canonical
            if not versions.has_key(default_lang):
                can_lang = versions.keys()[0]
            else:
                can_lang = default_lang
            can = getattr(self.context.getTranslation(can_lang), versions[can_lang], getattr(self.context, versions[can_lang], None))
            if can is None:
                raise "Canonical version of %s was not found!" %versions[can_lang]
            can.setCanonical()
            for lang in versions.keys():
                if lang == can_lang:
                    continue
                # Always look in the translated container first, before attempting to get thefile in the local container
                trans_obj = getattr(self.context.getTranslation(lang), versions[lang], getattr(self.context, versions[lang], None))
                if trans_obj is None:
                    raise "Translated object %s was not found!" %versions[lang]
                # invalidate all exisitng references
                # reason: we might have a new canonical version (if a file with the default language was
                # previously missing and is now uploaded)
                for x in trans_obj.getTranslations().values():
                    x[0].removeTranslationReference(trans_obj)
                    trans_obj.removeTranslationReference(x[0])
                if can.getTranslation(lang) is None:
                    trans_obj.addTranslationReference(can)

    def _guessLanguage(self, filename):
        """
        try to find a language abbreviation in the string
        acceptable is a two letter language abbreviation at the end of the 
        string prefixed by an _ just before the extension
        """
        if callable(filename):
            filename = filename()

        langs = self.plt.getSupportedLanguages()
        default_lang = self.plt.getDefaultLanguage()

        if len(filename)>3 and '.' in filename:
            elems = filename.split('.')
            name = ".".join(elems[:-1])
            if len(name)>3 and name[-3] in ['_', '-']:
                lang = name[-2:].strip()
                lang = lang.lower()
                if lang in langs:
                    namestem = name[:(len(name)-2)]
                    return lang, namestem, elems[-1]

        return default_lang, filename, ''