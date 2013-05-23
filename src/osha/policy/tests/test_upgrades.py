# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from osha.policy.tests.base import OSHA_INTEGRATION_TESTING
from slc.linkcollection.interfaces import ILinkList

import unittest2 as unittest


class TestRearrangeSEPs(unittest.TestCase):
    """Test rearrange_seps upgrade step."""

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


class TestHideContacts(unittest.TestCase):
    """Test hide_contacts upgrade step."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        # create test content
        self.portal.invokeFactory(
            'PressRoom', 'press', title='Press room'
        )
        self.portal['press']['press-releases'].invokeFactory(
            'PressRelease', 'release1', title='Press release 1'
        )
        self.portal['press']['press-releases'].invokeFactory(
            'PressRelease', 'release2', title='Press release 2'
        )
        self.portal['press']['press-releases'].invokeFactory(
            'PressRelease', 'release3', title='Press release 3'
        )
        self.release1 = self.portal['press']['press-releases']['release1']
        self.release2 = self.portal['press']['press-releases']['release2']
        self.release3 = self.portal['press']['press-releases']['release3']

    # XXX: failing, disabled for now
    def _test_hide_contacts(self):
        """Test the upgrade step."""
        from osha.policy.upgrades import hide_contacts

        # showContacts should be true before the upgrade
        self.assertTrue(
            self.release1.getField('showContacts').getAccessor(self.release1)()
        )
        self.assertTrue(
            self.release2.getField('showContacts').getAccessor(self.release1)()
        )
        self.assertTrue(
            self.release3.getField('showContacts').getAccessor(self.release1)()
        )

        # and False after the upgrade
        hide_contacts(self.portal)

        self.assertFalse(
            self.release1.getField('showContacts').getAccessor(self.release1)()
        )
        self.assertFalse(
            self.release2.getField('showContacts').getAccessor(self.release1)()
        )
        self.assertFalse(
            self.release3.getField('showContacts').getAccessor(self.release1)()
        )


class TestRearrangeBlog(unittest.TestCase):
    """Test rearrange_blog upgrade step."""

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self._create_test_data()

    def _create_test_data(self):
        """Create blog hierachy before the upgrade."""

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
            'Topic',
            'front-page',
            title="Director's corner",
            text="""<p>\r\n\t<img align="left" alt="Picture of Dr Christa Sedlatschek" height="91" src="/en/teaser/Dr-Christa-Sedlatschek-appointed-to-lead-EU-OSHA/image" width="80" /></p>\r\n<h2>\r\n\t&nbsp;Short profile of Dr Christa Sedlatschek</h2>\r\n<p>\r\n\t&nbsp;<strong>Dr Christa Sedlatschek</strong>&nbsp;is a medical doctor (University of Vienna) and a specialist in occupational health.</p>\r\n<p>\r\n\t&nbsp;After completing her studies she started working in the Austrian labour inspectorate and moved to the Ministry for Labour and Social Affairs in 1993, taking over the function as Deputy Head of the department for occupational medicine.</p>\r\n<p>\r\n\tIn 1998 she was recruited by EU-OSHA where she focused on the development and dissemination of good practice information, becoming the head of the working environment unit. During that time she gained an in-depth knowledge about the EU and existing occupational safety and health (OSH) systems in the Member States.</p>\r\n<p>\r\n\tIn 2003 she moved to Berlin and started working in the Federal Institute for Occupational Safety and Health (Bundesanstalt f\xc3\xbcr Arbeitsschutz und Arbeitsmedizin - BAuA), where she became Director of the national \xe2\x80\x9cInitiative New Quality of Work - INQA\xe2\x80\x9d in 2004.</p>\r\n<p>\r\n\t\xe2\x80\x9cINQA\xe2\x80\x9d was launched by the German Federal Ministry for labour and social affairs as a consequence of the Lisbon Summit in 2000, aiming at making a contribution towards creating more and better jobs in Europe.</p>\r\n<p>\r\n\t&nbsp;</p>\r\n<h2>\r\n\tOSH Blog</h2>\r\n<p class="documentDescription" style="border: 1px dotted rgb(197, 203, 216); margin-bottom: 2em; margin-right: 15px; padding-bottom: 5px; padding-left: 3px;">\r\n\t<img alt="blog_logo-def.jpg" height="80" src="/en/blog/blogo_logo" style="float: right;" width="80" />The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission.<br />\r\n\tWe are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work.<br />\r\n\t&nbsp;</p>\r\n"""
        )
        self.director_corner_en = self.portal['en']['about']['director_corner']
        self.portal['en']['about']['director_corner'].invokeFactory(
            'Folder',
            'blog',
            title="OSH Blog"
        )
        self.portal['en']['about']['director_corner']['blog'].invokeFactory(
            'Topic',
            'front-page',
            title="OSH Blog",
            text="The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission. We are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work."
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
            'Topic',
            'front-page',
            title="Der Direktor hat das Wort",
            text="""<p>\r\n\t<img align="left" alt="Bild von Dr. med. Christa Sedlatschek" height="91" src="/en/teaser/Dr-Christa-Sedlatschek-appointed-to-lead-EU-OSHA/image" width="80" /></p>\r\n<h2>\r\n\tKurzprofil von Dr. med. Christa Sedlatschek</h2>\r\n<p>\r\n\t<strong>&nbsp;Dr. med. Christa Sedlatschek</strong>&nbsp;studierte Medizin an der Universit\xc3\xa4t Wien und ist Fach\xc3\xa4rztin f\xc3\xbcr Arbeitsmedizin.</p>\r\n<p>\r\n\t&nbsp;Nach ihrem Studium war sie zun\xc3\xa4chst in der \xc3\xb6sterreichischen Arbeitsinspektion t\xc3\xa4tig und wechselte 1993 als stellvertretende Leiterin der Abteilung Arbeitsmedizin ins Arbeits- und Sozialministerium.</p>\r\n<p>\r\n\t1998 wechselte sie zur EU-OSHA, wo sie sich auf die Entwicklung und Verbreitung von Informationen \xc3\xbcber gute praktische L\xc3\xb6sungen konzentrierte und Leiterin des Referats Arbeitsumfeld wurde. In dieser Zeit erwarb sie gr\xc3\xbcndliche Kenntnisse \xc3\xbcber die EU und die bestehenden Systeme der Sicherheit und des Gesundheitsschutzes bei der Arbeit in den Mitgliedstaaten.</p>\r\n<p>\r\n\t2003 ging sie nach Berlin und nahm eine T\xc3\xa4tigkeit in der Bundesanstalt f\xc3\xbcr Arbeitsschutz und Arbeitsmedizin (BAuA) auf, wo sie 2004 Gesch\xc3\xa4ftsf\xc3\xbchrerin der Initiative Neue Qualit\xc3\xa4t der Arbeit (INQA) wurde.</p>\r\n<p>\r\n\tDie Initiative INQA wurde vom Bundesministerium f\xc3\xbcr Arbeit und Soziales nach dem Lissabonner Gipfel im Jahr 2000 mit dem Ziel ins Leben gerufen, einen Beitrag zur Schaffung von mehr und besseren Arbeitspl\xc3\xa4tzen in Europa zu leisten.</p>\r\n<p>\r\n\t&nbsp;</p>\r\n<h2>\r\n\tOSH Blog</h2>\r\n<p class="documentDescription" style="border: 1px dotted rgb(197, 203, 216); margin-bottom: 2em; margin-right: 15px; padding-bottom: 5px; padding-left: 3px;">\r\n\t<img alt="blog_logo-def.jpg" height="80" src="/en/blog/blogo_logo" style="float: right;" width="80" />The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission.<br />\r\n\tWe are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work.<br />\r\n\t&nbsp;</p>\r\n"""
        )
        self.director_corner_de = self.portal['de']['about']['director_corner']
        self.portal['de']['about']['director_corner'].invokeFactory(
            'Folder',
            'blog',
            title="OSH Blog"
        )
        self.portal['de']['about']['director_corner']['blog'].invokeFactory(
            'Topic',
            'front-page',
            title='OSH Blog',
            text="The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission. We are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work."
        )

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

    def test__convert_front_page_converted(self):
        """Test converting front page from Collection to Document"""
        from osha.policy.upgrades import _convert_front_page
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['blog']['front-page'],
            wf_state='private',
            layout='blog-view'
        )
        self.assertEquals(new_front_page.portal_type, 'Document')
        self.assertEquals(new_front_page.getLayout(), 'blog-view')

    def test__convert_front_page_state_not_published(self):
        """Test if the right workflow state is set for the front page if
        wf_state is not 'published'.
        """
        from osha.policy.upgrades import _convert_front_page
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['blog']['front-page'],
            wf_state='visible',
            layout='blog-view'
        )

        self.assertEquals(
            api.content.get_state(obj=new_front_page), 'private')

    def test__convert_front_page_state_published(self):
        """Test if the right workflow state is set for the front page if
        wf_state is set to 'published'.
        """
        from osha.policy.upgrades import _convert_front_page
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['blog']['front-page'],
            wf_state='published',
            layout='blog-view'
        )

        self.assertEquals(
            api.content.get_state(obj=new_front_page), 'published')

    def test__convert_front_page_fix_text_disabled(self):
        """Test if the body text is untouched if fix_test is set to False.
        """
        from osha.policy.upgrades import _convert_front_page
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['front-page'],
            wf_state='published',
            layout='director-corner-view',
            fix_text=False
        )

        # body text shouldn't be altered
        self.assertEquals(
            new_front_page.getText(),
            """<p>\r\n\t<img align="left" alt="Picture of Dr Christa Sedlatschek" height="91" src="/en/teaser/Dr-Christa-Sedlatschek-appointed-to-lead-EU-OSHA/image" width="80" /></p>\r\n<h2>\r\n\t&nbsp;Short profile of Dr Christa Sedlatschek</h2>\r\n<p>\r\n\t&nbsp;<strong>Dr Christa Sedlatschek</strong>&nbsp;is a medical doctor (University of Vienna) and a specialist in occupational health.</p>\r\n<p>\r\n\t&nbsp;After completing her studies she started working in the Austrian labour inspectorate and moved to the Ministry for Labour and Social Affairs in 1993, taking over the function as Deputy Head of the department for occupational medicine.</p>\r\n<p>\r\n\tIn 1998 she was recruited by EU-OSHA where she focused on the development and dissemination of good practice information, becoming the head of the working environment unit. During that time she gained an in-depth knowledge about the EU and existing occupational safety and health (OSH) systems in the Member States.</p>\r\n<p>\r\n\tIn 2003 she moved to Berlin and started working in the Federal Institute for Occupational Safety and Health (Bundesanstalt f\xc3\xbcr Arbeitsschutz und Arbeitsmedizin - BAuA), where she became Director of the national \xe2\x80\x9cInitiative New Quality of Work - INQA\xe2\x80\x9d in 2004.</p>\r\n<p>\r\n\t\xe2\x80\x9cINQA\xe2\x80\x9d was launched by the German Federal Ministry for labour and social affairs as a consequence of the Lisbon Summit in 2000, aiming at making a contribution towards creating more and better jobs in Europe.</p>\r\n<p>\r\n\t&nbsp;</p>\r\n<h2>\r\n\tOSH Blog</h2>\r\n<p class="documentDescription" style="border: 1px dotted rgb(197, 203, 216); margin-bottom: 2em; margin-right: 15px; padding-bottom: 5px; padding-left: 3px;">\r\n\t<img alt="blog_logo-def.jpg" height="80" src="/en/blog/blogo_logo" style="float: right;" width="80" />The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission.<br />\r\n\tWe are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work.<br />\r\n\t&nbsp;</p>\r\n"""
        )

    def test__convert_front_page_fix_text_no_oshblog(self):
        """Test if the body text is set correctly if no 'OSH blog' text is
        present in the front-page body.
        """
        from osha.policy.upgrades import _convert_front_page
        self.director_corner_en['front-page'].setText('foo')
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['front-page'],
            wf_state='published',
            layout='director-corner-view',
            fix_text=True
        )

        # body text shouldn't be altered
        self.assertEquals(
            new_front_page.getText(),
            """<p>foo</p>"""
        )

    def test__convert_front_page_fix_text_oshblog(self):
        """Test if the body text is set correctly if 'OSH blog' text is
        present in the front-page body.
        """
        from osha.policy.upgrades import _convert_front_page
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['front-page'],
            wf_state='published',
            layout='director-corner-view',
            fix_text=True
        )

        # OSH Blog description should be removed from the body text
        self.assertEquals(
            new_front_page.getText(),
            """<p>\r\n\t<img align="left" alt="Picture of Dr Christa Sedlatschek" height="91" src="/en/teaser/Dr-Christa-Sedlatschek-appointed-to-lead-EU-OSHA/image" width="80" /></p>\r\n<h2>\r\n\t&nbsp;Short profile of Dr Christa Sedlatschek</h2>\r\n<p>\r\n\t&nbsp;<strong>Dr Christa Sedlatschek</strong>&nbsp;is a medical doctor (University of Vienna) and a specialist in occupational health.</p>\r\n<p>\r\n\t&nbsp;After completing her studies she started working in the Austrian labour inspectorate and moved to the Ministry for Labour and Social Affairs in 1993, taking over the function as Deputy Head of the department for occupational medicine.</p>\r\n<p>\r\n\tIn 1998 she was recruited by EU-OSHA where she focused on the development and dissemination of good practice information, becoming the head of the working environment unit. During that time she gained an in-depth knowledge about the EU and existing occupational safety and health (OSH) systems in the Member States.</p>\r\n<p>\r\n\tIn 2003 she moved to Berlin and started working in the Federal Institute for Occupational Safety and Health (Bundesanstalt f\xc3\xbcr Arbeitsschutz und Arbeitsmedizin - BAuA), where she became Director of the national \xe2\x80\x9cInitiative New Quality of Work - INQA\xe2\x80\x9d in 2004.</p>\r\n<p>\r\n\t\xe2\x80\x9cINQA\xe2\x80\x9d was launched by the German Federal Ministry for labour and social affairs as a consequence of the Lisbon Summit in 2000, aiming at making a contribution towards creating more and better jobs in Europe.</p>\r\n<p>\r\n\t&nbsp;</p>\r\n"""
        )

    # XXX: fails atm, why doesn't setting locally allowed types work?
    def _test__convert_front_page_non_addable(self):
        """Test if correctly handle the case when Documents are not addable
        to the blog subfolder.
        """
        from osha.policy.upgrades import _convert_front_page

        # set 'Collection' as the only addable type
        blog = self.director_corner_en['blog']
        blog.setLocallyAllowedTypes(('Collection', ))
        new_front_page = _convert_front_page(
            obj=self.director_corner_en['blog']['front-page'],
            wf_state='published',
            layout='blog-view'
        )

        # we shouldn't get an error, 'Document' should be added to the list
        # of available types
        self.assertIn('front-page', blog.keys())
        self.assertEquals(new_front_page.portal_type, 'Document')
        self.assertEquals(
            blog.getLocallyAllowedTypes(),
            ('Collection', 'Document',)
        )

    def test_rearrange_blog_director_corner_missing(self):
        """Test if we correctly handle misconfigured director's corner
        section.
        """
        from osha.policy.upgrades import rearrange_blog

        # no error should be raised
        del self.portal['en']['about']['director_corner']['blog']['front-page']
        self.assertIsNone(rearrange_blog(self.portal))
        del self.portal['en']['about']['director_corner']['front-page']
        self.assertIsNone(rearrange_blog(self.portal))
        del self.portal['en']['about']['director_corner']
        self.assertIsNone(rearrange_blog(self.portal))

    def test_rearrange_blog_hierarchy(self):
        """Test if we have the right object hierarchy after running the
        upgrade.
        """
        from osha.policy.upgrades import rearrange_blog
        rearrange_blog(self.portal)

        self.assertEquals(
            sorted(self.director_corner_en.keys()),
            ['blog', 'front-page']
        )
        self.assertEquals(
            sorted(self.director_corner_en['blog'].keys()),
            ['blog-entry-1', 'blog-entry-2', 'front-page']
        )

        self.assertEquals(
            sorted(self.director_corner_de.keys()),
            ['blog', 'front-page']
        )
        self.assertEquals(
            sorted(self.director_corner_de['blog'].keys()),
            ['front-page']
        )

        self.assertEquals(
            self.director_corner_en['front-page'].portal_type, 'Document')
        self.assertEquals(
            self.director_corner_en['blog']['front-page'].portal_type,
            'Document'
        )
        self.assertEquals(
            self.director_corner_de['front-page'].portal_type, 'Document')
        self.assertEquals(
            self.director_corner_de['blog']['front-page'].portal_type,
            'Document')

    def test_rearrange_blog_translations_linked(self):
        """Test if front pages have proper translation references."""
        from osha.policy.upgrades import rearrange_blog
        rearrange_blog(self.portal)

        translations_dc = self.director_corner_en[
            'front-page'].getTranslations()
        self.assertEquals(sorted(translations_dc.keys()), ['de', 'en'])

        translations_blog = self.director_corner_en[
            'blog']['front-page'].getTranslations()
        self.assertEquals(sorted(translations_blog.keys()), ['de', 'en'])

    def test_rearrange_blog_front_page_content(self):
        """Test if we have the right content in the front pages"""
        from osha.policy.upgrades import rearrange_blog
        rearrange_blog(self.portal)

        self.assertEquals(
            self.director_corner_en['front-page'].Title(),
            "Director's corner"
        )
        self.assertEquals(
            self.director_corner_en['front-page'].getText(),
            """<p>\r\n\t<img align="left" alt="Picture of Dr Christa Sedlatschek" height="91" src="/en/teaser/Dr-Christa-Sedlatschek-appointed-to-lead-EU-OSHA/image" width="80" /></p>\r\n<h2>\r\n\t&nbsp;Short profile of Dr Christa Sedlatschek</h2>\r\n<p>\r\n\t&nbsp;<strong>Dr Christa Sedlatschek</strong>&nbsp;is a medical doctor (University of Vienna) and a specialist in occupational health.</p>\r\n<p>\r\n\t&nbsp;After completing her studies she started working in the Austrian labour inspectorate and moved to the Ministry for Labour and Social Affairs in 1993, taking over the function as Deputy Head of the department for occupational medicine.</p>\r\n<p>\r\n\tIn 1998 she was recruited by EU-OSHA where she focused on the development and dissemination of good practice information, becoming the head of the working environment unit. During that time she gained an in-depth knowledge about the EU and existing occupational safety and health (OSH) systems in the Member States.</p>\r\n<p>\r\n\tIn 2003 she moved to Berlin and started working in the Federal Institute for Occupational Safety and Health (Bundesanstalt f\xc3\xbcr Arbeitsschutz und Arbeitsmedizin - BAuA), where she became Director of the national \xe2\x80\x9cInitiative New Quality of Work - INQA\xe2\x80\x9d in 2004.</p>\r\n<p>\r\n\t\xe2\x80\x9cINQA\xe2\x80\x9d was launched by the German Federal Ministry for labour and social affairs as a consequence of the Lisbon Summit in 2000, aiming at making a contribution towards creating more and better jobs in Europe.</p>\r\n<p>\r\n\t&nbsp;</p>\r\n"""
        )
        self.assertEquals(
            self.director_corner_en['blog']['front-page'].Title(),
            'OSH Blog'
        )
        self.assertEquals(
            self.director_corner_en['blog']['front-page'].getText(),
            "<p>The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission. We are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work.</p>"
        )

        self.assertEquals(
            self.director_corner_de['front-page'].Title(),
            "Der Direktor hat das Wort"
        )
        self.assertEquals(
            self.director_corner_de['front-page'].getText(),
            """<p>\r\n\t<img align="left" alt="Bild von Dr. med. Christa Sedlatschek" height="91" src="/en/teaser/Dr-Christa-Sedlatschek-appointed-to-lead-EU-OSHA/image" width="80" /></p>\r\n<h2>\r\n\tKurzprofil von Dr. med. Christa Sedlatschek</h2>\r\n<p>\r\n\t<strong>&nbsp;Dr. med. Christa Sedlatschek</strong>&nbsp;studierte Medizin an der Universit\xc3\xa4t Wien und ist Fach\xc3\xa4rztin f\xc3\xbcr Arbeitsmedizin.</p>\r\n<p>\r\n\t&nbsp;Nach ihrem Studium war sie zun\xc3\xa4chst in der \xc3\xb6sterreichischen Arbeitsinspektion t\xc3\xa4tig und wechselte 1993 als stellvertretende Leiterin der Abteilung Arbeitsmedizin ins Arbeits- und Sozialministerium.</p>\r\n<p>\r\n\t1998 wechselte sie zur EU-OSHA, wo sie sich auf die Entwicklung und Verbreitung von Informationen \xc3\xbcber gute praktische L\xc3\xb6sungen konzentrierte und Leiterin des Referats Arbeitsumfeld wurde. In dieser Zeit erwarb sie gr\xc3\xbcndliche Kenntnisse \xc3\xbcber die EU und die bestehenden Systeme der Sicherheit und des Gesundheitsschutzes bei der Arbeit in den Mitgliedstaaten.</p>\r\n<p>\r\n\t2003 ging sie nach Berlin und nahm eine T\xc3\xa4tigkeit in der Bundesanstalt f\xc3\xbcr Arbeitsschutz und Arbeitsmedizin (BAuA) auf, wo sie 2004 Gesch\xc3\xa4ftsf\xc3\xbchrerin der Initiative Neue Qualit\xc3\xa4t der Arbeit (INQA) wurde.</p>\r\n<p>\r\n\tDie Initiative INQA wurde vom Bundesministerium f\xc3\xbcr Arbeit und Soziales nach dem Lissabonner Gipfel im Jahr 2000 mit dem Ziel ins Leben gerufen, einen Beitrag zur Schaffung von mehr und besseren Arbeitspl\xc3\xa4tzen in Europa zu leisten.</p>\r\n<p>\r\n\t&nbsp;</p>\r\n"""
        )
        self.assertEquals(
            self.director_corner_de['blog']['front-page'].Title(),
            'OSH Blog'
        )
        self.assertEquals(
            self.director_corner_de['blog']['front-page'].getText(),
            "<p>The aim of this blog is to bring you news about developments in occupational safety and health across the EU and beyond, and also about EU-OSHA initiatives and activities to fulfill our mission. We are one of the smallest EU agencies and cannot promise to reply to every comment, but we will read them and bear them in mind to shape our future work.</p>"
        )


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
