"""Test utils."""
from plone import api


def set_language(lang):
    """Change language settings."""
    ltool = api.portal.get_tool('portal_languages')
    defaultLanguage = lang
    supportedLanguages = [lang, 'en']
    ltool.manage_setLanguageSettings(
        defaultLanguage,
        supportedLanguages,
        setUseCombinedLanguageCodes=False
    )
    ltool.setLanguageBindings()
