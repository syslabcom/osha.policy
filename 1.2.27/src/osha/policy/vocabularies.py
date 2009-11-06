from zope.app.schema.vocabulary import IVocabularyFactory
from zope.interface import implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
from Products.PlacelessTranslationService import getTranslationService

from Acquisition import aq_get

from Products.CMFCore.utils import getToolByName



class CategoriesVocabulary(object):
    """Vocabulary factory for Categories (Subject).
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        # XXX This is evil. A vocabulary shouldn't be request specific.
        # The sorting should go into a separate widget.
        name = "subject"
        index = "Subject"
        catalog = getToolByName(context, 'portal_catalog')
        result = catalog.uniqueValuesFor(index)
        result = list(result)
        result.sort()
        pts = getTranslationService()
        terms = [SimpleTerm(k, title=pts.translate(domain="osha", msgid=k, context=context) ) for k in result]
        return SimpleVocabulary(terms)

CategoriesVocabularyFactory = CategoriesVocabulary()
