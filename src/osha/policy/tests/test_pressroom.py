from osha.policy.tests.base import OSHA_INTEGRATION_TESTING

import unittest2 as unittest


class TestPressroomHelper(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        # create test content and prepare helper variables
        self.portal = self.layer['portal']
        self.ltool = self.portal.portal_languages
        self.portal.invokeFactory(
            'Document', 'page1', title='Page 1'
        )
        self.portal.invokeFactory(
            'Document', 'page2', title='Page 2'
        )
        self.portal.invokeFactory(
            'PressRoom', 'press-room', title='Press room'
        )
        self.press_room = self.portal['press-room']
        self.press_room['press-releases'].invokeFactory(
            'PressRelease', 'press-release', title='Press release'
        )
        self.press_release = self.press_room['press-releases']['press-release']

    def test_getTranslatedReferences_constraints(self):
        """Test if the method correctly handles bad input."""

        helper = self.press_release.restrictedTraverse('pressroom_helper')

        # if we don't pass 'fieldname' parameter or we pass a non-existent
        # fieldname, we should get an error
        self.assertRaises(ValueError, helper.getTranslatedReferences)
        self.assertRaises(
            KeyError, helper.getTranslatedReferences, fieldname='foo')

    def test_getTranslatedReferences_results(self):
        """Test if we get correct results."""

        helper = self.press_release.restrictedTraverse('pressroom_helper')

        self.assertEqual(
            helper.getTranslatedReferences(fieldname='relatedLinks'), [])

        # now let's add some references (in this case we use
        # relatedLinks field)
        self.press_release.setRelatedLinks(
            [self.portal['page1'], self.portal['page2']])
        self.assertEqual(helper.getTranslatedReferences(
            fieldname='relatedLinks'),
            [self.portal['page1'], self.portal['page2']]
        )

    def test_getTranslatedReferences_translations(self):
        """Test if we get correct results when content is translated."""

        helper = self.press_release.restrictedTraverse('pressroom_helper')

        # add some references and translate one of them
        self.press_release.setRelatedLinks(
            [self.portal['page1'], self.portal['page2']])
        self.portal['page1'].addTranslation('sl')

        self.assertEqual(helper.getTranslatedReferences(
            fieldname='relatedLinks'),
            [self.portal['page1'], self.portal['page2']]
        )

        # now change the current language to 'sl'
        self.ltool.manage_setLanguageSettings(
            'sl', ['sl', 'en'], setUseCombinedLanguageCodes=False)
        self.ltool.setLanguageBindings()

        # we should get the translated page among results
        self.assertEqual(
            helper.getTranslatedReferences(fieldname='relatedLinks'),
            [self.portal['page1-sl'], self.portal['page2']]
        )

    def test_getContacts_context(self):
        """Test if the method correctly handles wrong context -
        we should be inside PressRoom object hiearachy for it to work.
        """
        # it should return None if we're not inside PressRoom
        helper = self.portal.restrictedTraverse('pressroom_helper')
        self.assertEqual(helper.getContacts(), None)

        # it should work if we are on Press release or Press room
        helper = self.press_room.restrictedTraverse('pressroom_helper')
        self.assertNotEqual(helper.getContacts(), None)
        helper = self.press_release.restrictedTraverse('pressroom_helper')
        self.assertNotEqual(helper.getContacts(), None)

    def test_getContacts_results(self):
        """Test if we get correct results."""

        helper = self.press_release.restrictedTraverse('pressroom_helper')

        self.assertEqual(helper.getContacts(), '')

        # add some contact info
        mutator = self.press_room.getField('contacts').getMutator(
            self.press_room)
        mutator(u'Chuck Norris chuck@norris.com')

        self.assertEqual(
            helper.getContacts(),
            u'Chuck Norris chuck@norris.com'
        )

    def test_getContacts_translations(self):
        """Test if we get correct results when content is translated."""

        # add some contact info
        mutator = self.press_room.getField('contacts').getMutator(
            self.press_room)
        mutator(u'Chuck Norris chuck@norris.com')

        # translate the press release and change the current language
        press_release_sl = self.press_release.addTranslation('sl')
        self.ltool.manage_setLanguageSettings(
            'sl', ['sl', 'en'], setUseCombinedLanguageCodes=False)
        self.ltool.setLanguageBindings()

        helper = press_release_sl.restrictedTraverse('pressroom_helper')

        # we should get contact info from the canonical PressRoom object if
        # there is no press room translation available
        self.assertEqual(
            helper.getContacts(), u'Chuck Norris chuck@norris.com')

        # now add a press room translation
        self.press_room.addTranslation('sl')
        mutator = self.portal['press-room-sl'].getField(
            'contacts').getMutator(self.portal['press-room-sl'])
        mutator(u'Martin Krpan martin@krpan.com')

        # we should get contact info from the translation
        self.assertEqual(
            helper.getContacts(), u'Martin Krpan martin@krpan.com')


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class(es) above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
