import unittest2 as unittest

from DateTime import DateTime
from Products.PloneHelpCenter.config import ADD_CENTER_PERMISSION

from osha.policy.tests.base import OSHA_INTEGRATION_TESTING


class TestOshaHelpCenter(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def _add_faq(self, folder, faq_title, subcategory=None):
        wft = self.portal.portal_workflow
        wf_status = {'helpcenter_workflow': (
                {'action': None,
                 'review_state': 'published',
                 'comments': '', 'actor':
                 'test_user_1_',
                 'time': DateTime('2011/06/21 15:37:19.954 GMT+2')},
                'published')}

        faq_id = folder.invokeFactory("HelpCenterFAQ", faq_title)
        faq = folder[faq_id]
        if subcategory:
            faq.subcategory = subcategory
            faq.Subject = subcategory
        wft.setStatusOf("helpcenter_workflow", faq, wf_status)
        faq.reindexObject()

    def setUp(self):
        self.portal = self.layer['portal']
        self.folder = self.portal['folder']
        self.portal.manage_permission(ADD_CENTER_PERMISSION, ['Owner', ])

        self.folder.invokeFactory("HelpCenter", "faqs")
        self.folder.faqs.invokeFactory("HelpCenterFAQFolder", "other-faqs")
        self.folder.faqs.invokeFactory("HelpCenterFAQFolder",
                                       "general-information")
        general_info_faqs = self.folder.faqs["general-information"]
        other_faqs = self.folder.faqs["other-faqs"]

        self._add_faq(general_info_faqs, "general-faq")
        self._add_faq(other_faqs, "agriculture-faq",
                      subcategory=(u'agriculture',
                                   u'agriculture::special_groups'))
        self._add_faq(other_faqs, "agriculture-faq2",
                      subcategory=(u'agriculture',))
        self._add_faq(other_faqs, "accident-prevention-faq",
                      subcategory=(u'accident_prevention',))

    def test_general_faqs(self):
        import pdb;pdb.set_trace()
        osha_helpcenter_view = self.portal.unrestrictedTraverse(
            "/plone/Members/test_user_1_/faqs/osha_help_center_view")

        faq_ids = [i.id for i in osha_helpcenter_view.faqs]
        self.assertEquals(faq_ids, ['general-faq'])

    def test_top_level_categories(self):
        osha_helpcenter_view = self.portal.unrestrictedTraverse(
            "/plone/Members/test_user_1_/faqs/osha_help_center_view")
        self.assertEquals(osha_helpcenter_view.get_categories().keys(),
                          ['accident_prevention', 'agriculture'])

    def test_sub_level_faqs(self):
        osha_helpcenter_view = self.portal.unrestrictedTraverse(
            "/plone/Members/test_user_1_/faqs/osha_help_center_view")
        osha_helpcenter_view.request.form["subcategory"] = "agriculture"
        osha_helpcenter_view.__init__(self.folder,
            osha_helpcenter_view.request)

        faq_ids = [i.id for i in osha_helpcenter_view.faqs]
        self.assertEquals(faq_ids, ['agriculture-faq', 'agriculture-faq2'])

    def test_sub_level_categories(self):
        osha_helpcenter_view = self.portal.unrestrictedTraverse(
            "/plone/Members/test_user_1_/faqs/osha_help_center_view")
        osha_helpcenter_view.request.form["subcategory"] = "agriculture"
        osha_helpcenter_view.__init__(self.folder,
            osha_helpcenter_view.request)

        subcat_keys = osha_helpcenter_view.get_subcategories(
            "agriculture").keys()
        self.assertEquals(subcat_keys, ['agriculture::special_groups'])


def test_suite():
    """This sets up a test suite that actually runs the tests in
    the class above.
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
