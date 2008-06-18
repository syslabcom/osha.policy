# Oh my god how I hate this. Another patch. But ATVocabulary Manager allows 
# subtree searches only for tree vocabularies and not for VDEX
# But we want the multilingual XML interchangeability plus subtree searches
# And [jens] does not want to integrate this :(

#import logging
#
##def getTermKey(self):
##    """
##    returns the Key / Identifier of the term
##    """
##    return self.getIdentifier()
#    
#def getTermKeyPath(self):
#    path = [self.getTermKey(),]
#    actTerm = self
#    while actTerm.aq_parent.portal_type != 'VdexFileVocabulary' \
#              and hasattr(actTerm.aq_parent, 'getTermKey'):
#        path.append(actTerm.aq_parent.getTermKey())
#        actTerm = actTerm.aq_parent
#
#    path.reverse()
#    return path            
#    
##def SearchableText(self):
##    arr = []
##    arr.append(self.Title())    
##    arr.append(self.Description())    
##    return " ".join(arr)
#    
#    
#try:
#    logger = logging.getLogger('OSHA Patches')
#    logger.info("Patching ATVM")
#    from Products.ATVocabularyManager.types.vdex.term import VdexTerm
##    VdexTerm.getTermKey = getTermKey
#    VdexTerm.getTermKeyPath = getTermKeyPath
#    #VdexTerm.SearchableText = SearchableText
    
from imsvdex.vdex import VDEXManager, VDEXError

def _getManager(self, reset=False, returnerror=False):
    """takes the given file and returns an initialized VDEXManager."""
    if reset and hasattr(self, '_v_vdexmanager'):
        del self._v_vdexmanager
    lang = self._getLanguage()
    _v_vdexmanager = getattr(self, '_v_vdexmanager', {})
    manager = _v_vdexmanager.get(lang, None)
    if manager is not None:
        return manager
    field = self.getField('vdex')
    data = field.getRaw(self)
    try:
        manager = VDEXManager(str(data), lang=lang)
    except VDEXError, e:
        if not returnerror:                
            return None
        return str(e)
    # here is the bug. it is vdexmanager, not manager    
    _v_vdexmanager[lang] = manager
    self._v_vdexmanager = _v_vdexmanager
    return manager
    
from Products.ATVocabularyManager.types.vdex.vocabularyxml import IMSVDEXVocabulary
IMSVDEXVocabulary._getManager = _getManager
    
