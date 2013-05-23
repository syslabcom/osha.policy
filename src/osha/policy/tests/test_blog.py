# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from osha.policy.tests.utils import set_language
from zope.interface import alsoProvides

import unittest2 as unittest


class BlogTestCase(unittest.TestCase):
    """Test class for testing blog views."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self._create_test_data()

        # enable osha.theme theme layer
        from osha.theme.browser.interfaces import IOSHAThemeLayer
        alsoProvides(self.layer['request'], IOSHAThemeLayer)

    def _create_test_data(self):
        """Create blog hierachy."""

        # create 'en' content
        self.portal.invokeFactory(
            'Folder', 'en', title='English Folder'
        )
        self.portal['en'].invokeFactory(
            'Folder', 'about', title='About us'
        )
        self.portal['en']['about'].invokeFactory(
            'Folder', 'director_corner', title="Director's corner"
        )
        self.portal['en']['about']['director_corner'].invokeFactory(
            'Document',
            'front-page',
            title="Director's corner",
            description="Director's description",
            text="Director' corner text"
        )
        self.director_corner_en = self.portal['en']['about']['director_corner']
        self.portal['en']['about']['director_corner'].invokeFactory(
            'Folder', 'blog', title="OSH Blog"
        )
        self.portal['en']['about']['director_corner']['blog'].invokeFactory(
            'Document',
            'front-page',
            title="OSH Blog",
            description="OSH Blog description",
            text="OSH Blog text"
        )
        self.portal['en']['about']['director_corner']['blog'].invokeFactory(
            'Blog Entry', 'blog-entry-1', title="Blog Entry 1"
        )
        self.portal['en']['about']['director_corner']['blog']['blog-entry-1'].processForm()
        self.portal['en']['about']['director_corner']['blog'].invokeFactory(
            'Blog Entry', 'blog-entry-2', title="Blog Entry 2"
        )
        self.portal['en']['about']['director_corner']['blog']['blog-entry-2'].processForm()

        # create 'de' content
        self.portal.invokeFactory(
            'Folder', 'de', title='German Folder'
        )
        self.portal['de'].invokeFactory(
            'Folder', 'about', title='Über uns'
        )
        self.portal['de']['about'].invokeFactory(
            'Folder', 'director_corner', title="Der Direktor hat das Wort"
        )
        self.portal['de']['about']['director_corner'].invokeFactory(
            'Document',
            'front-page',
            title="Der Direktor hat das Wort",
            description="Der Direktor hat das Wort description",
            text="Der Direktor hat das Wort text"
        )
        self.director_corner_de = self.portal['de']['about']['director_corner']
        self.portal['de']['about']['director_corner'].invokeFactory(
            'Folder', 'blog', title="OSH Blog"
        )
        self.portal['de']['about']['director_corner']['blog'].invokeFactory(
            'Document',
            'front-page',
            title='OSH Blog',
            description="OSH Blog description (de)",
            text="OSH Blog text (de)"
        )
        self.portal['de']['about']['director_corner']['blog'].invokeFactory(
            'Blog Entry', 'blog-entry-1-de', title="Blog Entry 1 (de)"
        )
        self.portal['de']['about']['director_corner']['blog']['blog-entry-1-de'].processForm()


        # Set translations
        self.portal['de'].setLanguage('de')
        self.portal['de'].addTranslationReference(self.portal['en'])
        self.portal['de']['about'].setLanguage('de')
        self.portal['de']['about'].addTranslationReference(self.portal['en']['about'])
        self.portal['de']['about']['director_corner'].setLanguage('de')
        self.portal['de']['about']['director_corner'].addTranslationReference(self.portal['en']['about']['director_corner'])
        self.portal['de']['about']['director_corner']['front-page'].setLanguage('de')
        self.portal['de']['about']['director_corner']['front-page'].addTranslationReference(self.portal['en']['about']['director_corner']['front-page'])
        self.portal['de']['about']['director_corner']['blog'].setLanguage('de')
        self.portal['de']['about']['director_corner']['blog'].addTranslationReference(self.portal['en']['about']['director_corner']['blog'])
        self.portal['de']['about']['director_corner']['blog']['front-page'].setLanguage('de')
        self.portal['de']['about']['director_corner']['blog']['front-page'].addTranslationReference(self.portal['en']['about']['director_corner']['blog']['front-page'])
        self.portal['de']['about']['director_corner']['blog']['blog-entry-1-de'].setLanguage('de')
        self.portal['de']['about']['director_corner']['blog']['blog-entry-1-de'].addTranslationReference(self.portal['en']['about']['director_corner']['blog']['blog-entry-1'])


class TestBlogView(BlogTestCase):
    """Test the blog view."""

    def setUp(self):
        super(TestBlogView, self).setUp()

        # Set helper variables
        self.view_en = self.director_corner_en['blog']['front-page'].restrictedTraverse('blog-view')
        self.view_de = self.director_corner_de['blog']['front-page'].restrictedTraverse('blog-view')

    def test__get_blog_items_no_folder(self):
        """Test getting the blog items if no folder is given."""
        self.assertIsNone(self.view_en._get_blog_items())

    def test__get_blog_items_results(self):
        """Test getting the blog items."""
        blog_items_en = self.view_en._get_blog_items(
            folder=self.director_corner_en['blog'])
        set_language('de')
        blog_items_de = self.view_de._get_blog_items(
            folder=self.director_corner_de['blog'])

        self.assertEquals(
            [item.getId() for item in blog_items_en],
            ['blog-entry-1', 'blog-entry-2']
        )
        self.assertEquals(
            [item.getId() for item in blog_items_de],
            ['blog-entry-1-de', 'blog-entry-2']
        )

    def test_blog_items_results(self):
        """Test getting the blog items."""
        blog_items_en = self.view_en.blog_items()
        set_language('de')
        blog_items_de = self.view_de.blog_items()

        self.assertEquals(
            [item.getId() for item in blog_items_en],
            ['blog-entry-1', 'blog-entry-2']
        )
        self.assertEquals(
            [item.getId() for item in blog_items_de],
            ['blog-entry-1-de', 'blog-entry-2']
        )


class TestDirectorCornerView(BlogTestCase):
    """Test the Director's corner view."""

    def setUp(self):
        super(TestDirectorCornerView, self).setUp()

        # Set helper variables
        self.view_en = self.director_corner_en['front-page'].restrictedTraverse('director-corner-view')
        self.view_de = self.director_corner_de['front-page'].restrictedTraverse('director-corner-view')

    def test_blog_items_results(self):
        """Test getting the blog items."""
        blog_items_en = self.view_en.blog_items()
        set_language('de')
        blog_items_de = self.view_de.blog_items()

        self.assertEquals(
            [item.getId() for item in blog_items_en],
            ['blog-entry-1', 'blog-entry-2']
        )
        self.assertEquals(
            [item.getId() for item in blog_items_de],
            ['blog-entry-1-de', 'blog-entry-2']
        )

    def test_blog_intro_no_front_page(self):
        """Testing getting the blog intro if there is no front page."""
        del self.director_corner_en['blog']['front-page']

        # there should be no error
        self.assertIsNone(self.view_en.blog_intro())

    def test_blog_intro(self):
        """Test getting the blog intro from the blog subfolder front page."""
        self.assertEquals(
            self.view_en.blog_intro(),
            '<p>OSH Blog text</p>'
        )
        set_language('de')
        self.assertEquals(
            self.view_de.blog_intro(),
            '<p>OSH Blog text (de)</p>'
        )


class TestBlogRssView(BlogTestCase):
    """Test the Blog rss view."""

    def setUp(self):
        super(TestBlogRssView, self).setUp()

        # Set helper variables
        self.view_en = self.director_corner_en['blog'].restrictedTraverse(
            'blog-rss')
        self.view_de = self.director_corner_de['blog'].restrictedTraverse(
            'blog-rss')

    def test_blog_items_results(self):
        """Test getting the blog items."""
        blog_items_en = self.view_en.blog_items()
        set_language('de')
        blog_items_de = self.view_de.blog_items()

        self.assertEquals(
            [item.getId() for item in blog_items_en],
            ['blog-entry-1', 'blog-entry-2']
        )
        self.assertEquals(
            [item.getId() for item in blog_items_de],
            ['blog-entry-1-de', 'blog-entry-2']
        )


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
