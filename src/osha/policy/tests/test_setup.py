import unittest2 as unittest

from osha.policy.tests.base import OSHA_FUNCTIONAL_TESTING, startZServerSSH
import osha.policy as POLICY

from Products.CMFCore.utils import getToolByName


class TestSetup(unittest.TestCase):

    layer = OSHA_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.workflow = getToolByName(self.portal, 'portal_workflow')
        self.acl_users = getToolByName(self.portal, 'acl_users')
        self.types = getToolByName(self.portal, 'portal_types')

    # TODO: #4479 re-enable once osha.theme is integrated in the tests
    # def test_portal_title(self):
    #     self.assertEquals("OSHA - Your network to a safer and healthier working environment", self.portal.getProperty('title'))

    # TODO: #4479 re-enable once osha.theme is integrated in the tests
    # def test_portal_description(self):
    #     self.assertEquals("Global site - Your global gateway to a safer and healthier working environment", self.portal.getProperty('description'))

    def test_policy_basics(self):
        self.failUnless(POLICY.PROJECTNAME == 'OSHA 3.0')

    #def test_role_added(self):
    #    self.failUnless("StaffMember", self.portal.validRoles())

    def test_workflow_installed(self):
        self.failUnless('osh_workflow' in self.workflow.objectIds())

    def test_workflows_mapped(self):
        self.assertEquals(('osh_workflow',), self.workflow.getDefaultChain())
        for portal_type, chain in self.workflow.listChainOverrides():
            if portal_type in ('Folder', 'Large Plone Folder', 'Topic',):
                self.assertEquals(('folder_workflow',), chain)

    #def test_view_permisison_for_staffmember(self):
    #    # The API of the permissionsOfRole() function sucks - it is bound too
    #    # closely up in the permission management screen's user interface
    #    self.failUnless('View' in [r['name'] for r in 
    #                            self.portal.permissionsOfRole('Reader') if r['selected']])
    #    self.failUnless('View' in [r['name'] for r in 
    #                            self.portal.permissionsOfRole('StaffMember') if r['selected']])

    #def test_staffmember_group_added(self):
    #    self.assertEquals(1, len(self.acl_users.searchGroups(name='Staff')))

    # TODO: #4479 re-enable once osha.theme is integrated in the tests
    # def test_portaltypes_installed(self):
    #     self.failUnless('CallForContractors' in self.types.objectIds())
    #     self.failUnless('CaseStudy' in self.types.objectIds())
    #     self.failUnless('OSH_Link' in self.types.objectIds())
    #     #self.failUnless('PressRoom' in self.types.objectIds())
    #     self.failUnless('PublicJobVacancy' in self.types.objectIds())
    #     self.failUnless('RichDocument' in self.types.objectIds())
    #     self.failUnless('VocabularyLibrary' in self.types.objectIds())

    #def test_plain_document_disabled(self):
    #    # the internal name for "Page" is "Document"
    #    document_fti = getattr(self.types, 'Document')
    #    self.failIf(document_fti.global_allow)

    #def test_richdocument_renamed_to_page(self):
    #    rich_document_fti = getattr(self.types, 'RichDocument')
    #    self.assertEquals("Web page", rich_document_fti.title)

    # TODO: #4479 re-enable once osha.theme is integrated in the tests
    # def test_theme_installed(self):
    #     skins = getToolByName(self.portal, 'portal_skins')
    #     layer = skins.getSkinPath('OSHA Plone Theme')
    #     self.failUnless('osha_theme_custom_templates' in layer)
    #     self.assertEquals('OSHA Plone Theme', skins.getDefaultSkin())

    def test_types_versioned(self):
        repository = getToolByName(self.portal, 'portal_repository')
        versionable_types = repository.getVersionableContentTypes()
        for type_id in ('RichDocument', 'Document'):
            self.failUnless(type_id in versionable_types)

    def test_navtree_settings(self):
        nprops = self.portal.portal_properties.navtree_properties
        metatypes = ['AliasVocabulary'
                     , 'ATBooleanCriterion'
                     # XXX: fill in the rest
                     ]
        for m in metatypes:
            self.failIf(m not in nprops.metaTypesNotToList)
        self.failIf(nprops.sitemapDepth != 3)
        self.failIf(nprops.currentFolderOnlyInNavtree is not False)
        self.failIf(nprops.includeTop is not True)
        self.failIf(nprops.topLevel != 0)
        self.failIf(nprops.bottomLevel != 4)
        self.failIf(nprops.sitemapDepth != 3)
        self.failIf(nprops.showAllParents is not True)
        # XXX: test metatypes not to list

    def test_siteproperties_settings(self):
        sprops = self.portal.portal_properties.site_properties
        # XXX: 

    #def test_enquiry_action_installed(self):
    #    self.failUnless('contact' in self.portal.portal_actions.site_actions.objectIds())
