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
#        print "RenameLanguageFiles"
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
        for item in can.objectItems(TYPES):
            lang, namestem, suffix = self._guessLanguage(item[0])
            if item[1].Language()!= lang:
                item[1].setLanguage(lang)
                filenames.append(item[0])

        message = u'Set language according to suffix on these files:\n' +', '.join(filenames) 

        path = obj.absolute_url()
        getToolByName(obj, 'plone_utils').addPortalMessage(message)
        self.request.RESPONSE.redirect(path)



    def _guessLanguage(self, filename):
        """
        try to find a language abbreviation in the string
        acceptable is a two letter language abbreviation at the end of the 
        string prefixed by an _ just before the extension
        """
        if callable(filename):
            filename = filename()
    
        langs = self.plt.getSupportedLanguages()
    
        if len(filename)>3 and '.' in filename:
            elems = filename.split('.')
            name = ".".join(elems[:-1])
            if len(name)>3 and name[-3] in ['_', '-']:
                lang = name[-2:].strip()
                lang = lang.lower()
                if lang in langs:
                    namestem = name[:(len(name)-2)]
                    return lang, namestem, elems[-1]
    
        return '', filename, ''