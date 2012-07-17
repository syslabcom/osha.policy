from Products.Archetypes.interfaces.base import IBaseContent
from plone.indexer.decorator import indexer
from osha.theme.browser.vocabulary import get_vocabulary_path


@indexer(IBaseContent)
def nace(obj):
    return get_vocabulary_path(obj, 'nace')

@indexer(IBaseContent)
def target_user_groups(obj):
    return obj.getField('target_user_groups').getAccessor(obj)()

@indexer(IBaseContent)
def subcategory(obj):
    return get_vocabulary_path(obj, 'subcategory')

@indexer(IBaseContent)
def osha_metadata(obj):
    return get_vocabulary_path(obj, 'osha_metadata')

@indexer(IBaseContent)
def occupation(obj):
    return get_vocabulary_path(obj, 'occupation')

@indexer(IBaseContent)
def multilingual_thesaurus(obj):
    return get_vocabulary_path(obj, 'multilingual_thesaurus')

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
