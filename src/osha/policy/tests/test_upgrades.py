import unittest2 as unittest

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from slc.linkcollection.interfaces import ILinkList


class TestRearrangeSEPs(unittest.TestCase):
    """Test the rearrange SEPs upgrade step."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self._create_test_data()

    def _create_test_data(self):
        """ """
        self.folder = self.portal.folder

        # Create a default page for the folder
        self.folder.invokeFactory(
            'Document',
            'index_html',
            title='Default page',
            text='I haz links.'
        )
        self.index_html = self.folder['index_html']

        # Create linked content
        self.folder.invokeFactory(
            'Document',
            'linked1',
            title='Linked 1',
            text='I haz a foo.'
        )
        self.folder.invokeFactory(
            'Document',
            'linked2',
            title='Linked 2',
            text='I haz a bar.'
        )
        links = ILinkList(self.folder['index_html'])
        links.urls = [
            self.folder['linked1'].absolute_url(),
            self.folder['linked2'].absolute_url(),
        ]

        # Create translations of the folder and default page
        self.folder_de = self.folder.addTranslation('de')
        self.index_html_de = self.folder['index_html'].addTranslation('de')
        self.index_html_de.setText('Ich habe links.')

        # Create linked content for translations as well
        self.folder_de.invokeFactory(
            'Document',
            'linked1-de',
            title='Linked 1 de',
            text='Ich habe ein foo.'
        )
        self.folder_de.invokeFactory(
            'Document',
            'linked2-de',
            title='Linked 2 de',
            text='Ich habe ein bar.'
        )
        links_de = ILinkList(self.index_html_de)
        links_de.urls = [
            self.folder_de['linked1-de'].absolute_url(),
            self.folder_de['linked2-de'].absolute_url(),
        ]

    def test_rearrange_seps(self):
        """Test the upgrade step."""
        from osha.policy.upgrades import rearrange_seps

        # Run the upgrade step
        items = ['/'.join(self.folder.getPhysicalPath())]
        rearrange_seps(self.portal, items)

        # The body text of default page of the folder and translated folder
        # should be properly set, with link order preserved
        self.assertEqual(
            self.index_html.getText(),
            '<p>I haz links.</p>' \
            '<h2 class="linkcollection">Linked 1</h2><p>I haz a foo.</p>' \
            '<h2 class="linkcollection">Linked 2</h2><p>I haz a bar.</p>'
        )

        self.assertEqual(
            self.index_html_de.getText(),
            '<p>Ich habe links.</p>' \
            '<h2 class="linkcollection">Linked 1 de</h2><p>Ich habe ein ' \
            'foo.</p><h2 class="linkcollection">Linked 2 de</h2>' \
            '<p>Ich habe ein bar.</p>'
        )

        # Objects that were previously linked to should be deleted
        self.assertNotIn('linked1', self.folder.keys())
        self.assertNotIn('linked2', self.folder.keys())
        self.assertNotIn('linked1-de', self.folder_de.keys())
        self.assertNotIn('linked2-de', self.folder_de.keys())


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
