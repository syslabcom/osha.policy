from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.PlacelessTranslationService import getTranslationService
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
        result = catalog.uniqueValuesFor(index)
        result = list(result)
        result.sort()
        pts = getTranslationService()
        terms = [SimpleTerm(k, title=pts.translate(domain="osha", msgid=k, context=context) ) for k in result]

        return SimpleVocabulary(terms)

CategoriesVocabularyFactory = CategoriesVocabulary()
