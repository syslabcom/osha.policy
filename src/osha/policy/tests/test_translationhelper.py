from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest2 as unittest


class TestTranslationHelper(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.view = self.portal.restrictedTraverse('@@translation-helper')
        self._create_content()
        self._set_language()

    def _set_language(self):
        """Change language to 'de'"""
        ltool = getToolByName(self.portal, 'portal_languages')
        defaultLanguage = 'de'
        supportedLanguages = ['de', 'en']
        ltool.manage_setLanguageSettings(
            defaultLanguage,
            supportedLanguages,
            setUseCombinedLanguageCodes=False
        )
        ltool.setLanguageBindings()

    def _create_content(self):
        """Create content for testing."""
        self.portal.invokeFactory(
            'Folder', 'en', title='English Folder'
        )
        self.portal['en'].invokeFactory(
            'Folder', 'subfolder1', title='English Subfolder'
        )
        self.portal['en']['subfolder1'].invokeFactory(
            'Document', 'page1', title='English Page 1'
        )
        self.portal['en']['subfolder1'].invokeFactory(
            'Document', 'page2', title='English Page 2'
        )
        self.portal.invokeFactory(
            'Folder', 'de', title='German Folder'
        )
        self.portal['de'].invokeFactory(
            'Folder', 'subfolder1', title='German Subfolder'
        )
        self.portal['de']['subfolder1'].invokeFactory(
            'Document', 'page1', title='German Page 1'
        )

    def test_find_default_invalid_parameters(self):
        """Check that we correctly handle invalid parameters."""

        # invalid url
        result = self.view.find_default('http://foo')
        self.assertIsNone(result)

        # non-existing language
        result = self.view.find_default(
            'http://nohost/plone/de/subfolder1/page2',
            default='it'
        )
        self.assertIsNone(result)

    def test_find_default_no_results(self):
        """Try to find an object that is not available in default language.
        """
        result = self.view.find_default(
            'http://nohost/plone/de/subfolder1/foo')
        self.assertIsNone(result)

    def test_find_default_results(self):
        """Try to find an object that is available in the default languagage.
        """
        result = self.view.find_default(
            'http://nohost/plone/de/subfolder1/page2')
        self.assertEqual(
            result.absolute_url(),
            'http://nohost/plone/en/subfolder1/page2'
        )

    def test_get_fallback_url_invalid_parameters(self):
        """Check that we correctly handle invalid parameters."""

        # invalid url
        result = self.view.get_fallback_url('http://foo')
        self.assertIsNone(result)

    def test_get_fallback_url_non_existing_url(self):
        """Testing getting the fallback url for a non-existing url."""

        # if no object in current language has been found, it should return
        # portal url
        result = self.view.get_fallback_url('http://nohost/plone/foo/bar/baz')
        self.assertEqual(result, 'http://nohost/plone')

    def test_get_fallback_url_existing_url(self):
        """Testing getting the fallback url."""

        # foo is not available, but it should fallback to its parent
        result = self.view.get_fallback_url(
            'http://nohost/plone/de/subfolder1/foo')
        self.assertEqual(result, 'http://nohost/plone/de/subfolder1')

        result = self.view.get_fallback_url(
            'http://nohost/plone/de/foo/bar')
        self.assertEqual(result, 'http://nohost/plone/de')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
