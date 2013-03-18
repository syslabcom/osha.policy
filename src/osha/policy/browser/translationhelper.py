from osha.policy.browser.interfaces import ITranslationHelper
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements


class TranslationHelper(BrowserView):
    implements(ITranslationHelper)

    def find_default(self, url, default='en'):
        """This method tries to find an object in the default language, if the
        object wasn't found in the selected language. It does this by looking
        for an object with the same relative path in the default language
        folder.

        For example, if https://osha.europa.eu/de/about/contact_us isn't
        found, it will try to get https://osha.europa.eu/en/about/contact_us.

        :param url: absolute url of the object that was not found
        :param default: folder in which to look for the object, defaults to
            'en'
        :returns: Object in the default language, if found, otherwise None
        """
        portal = self.context.portal_url.getPortalObject()
        portal_url = portal.absolute_url()

        if not url.startswith(portal_url):
            return

        # convert to relative url and change the lang folder
        relative_url = url.replace(portal_url, '').strip('/')
        default_url = '/'.join([default] + relative_url.split('/')[1:])

        try:
            default_obj = portal.restrictedTraverse(default_url)
        except (AttributeError, KeyError):
            # the default version of the object was not found
            return

        return default_obj
