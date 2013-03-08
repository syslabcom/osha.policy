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

        langtool = getToolByName(self.context, 'portal_languages')
        preferred = langtool.getPreferredLanguage()
        default_url = url.replace(preferred, default)

        portal = self.context.portal_url.getPortalObject()
        relative_url = default_url.replace(
            portal.absolute_url(), '').strip('/')

        try:
            default_obj = portal.restrictedTraverse(relative_url)
        except (AttributeError, KeyError):
            # the default version of the object was not found
            return

        return default_obj
