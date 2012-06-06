from Products.Archetypes.interfaces.base import IBaseContent
from plone.indexer.decorator import indexer


@indexer(IBaseContent)
def nace(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('nace')

@indexer(IBaseContent)
def target_user_groups(obj):
    return obj.getField('target_user_groups').getAccessor(obj)()

@indexer(IBaseContent)
def subcategory(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('subcategory')

@indexer(IBaseContent)
def osha_metadata(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('osha_metadata')

@indexer(IBaseContent)
def occupation(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('occupation')

@indexer(IBaseContent)
def multilingual_thesaurus(obj):
    return obj.restrictedTraverse('@@getVocabularyPath')('multilingual_thesaurus')

@indexer(IBaseContent)
def lex_section(obj):
    return obj.getField('lex_section').getAccessor(obj)()

@indexer(IBaseContent)
def ero_topic(obj):
    return obj.getField('ero_topic').getAccessor(obj)()

@indexer(IBaseContent)
def ero_target_group(obj):
    return obj.getField('ero_target_group').getAccessor(obj)()

@indexer(IBaseContent)
def country(obj):
    return obj.getField('country').getAccessor(obj)()

@indexer(IBaseContent)
def cas(obj):
    return obj.getField('cas').getAccessor(obj)()

@indexer(IBaseContent)
def isNews(obj):
    return obj.getField('isNews').getAccessor(obj)()
