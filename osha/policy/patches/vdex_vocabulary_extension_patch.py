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
    
except:
    pass
    