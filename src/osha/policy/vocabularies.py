from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.Archetypes.interfaces import IVocabulary
from zope.i18n import translate
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName



class CategoriesVocabulary(object):
    """Vocabulary factory for Categories (Subject), translated in the osha-domain.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getSite()

        index = "Subject"
        catalog = getToolByName(context, 'portal_catalog')
        language = getToolByName(context, 'portal_languages').getPreferredLanguage()
        result = catalog.uniqueValuesFor(index)
        result = list(result)
        result.sort()
        terms = [SimpleTerm(k, title=translate(domain="osha", msgid=k, context=context,
            target_language=language) ) for k in result]

        return SimpleVocabulary(terms)

CategoriesVocabularyFactory = CategoriesVocabulary()


class ProviderVocabulary(object):
    """ Vocabulary for remoteProvider """
    implements(IVocabulary)

    def getVocabularyDict(self):
        """Build vocabulary dict
        """
        context = getSite()
        pc = getToolByName(context, 'portal_catalog')
        provRes = pc(portal_type='Provider', Language='all')
        results = dict(nocat=('No specific category', dict()))
        for res in provRes:
            title = res.Title
            results['nocat'][1][res.UID] = (title, None)
        return results

