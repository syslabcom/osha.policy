from osha.policy.browser.interfaces import ITranslationHelper
from Products.Five import BrowserView
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

        if 'resolveuid' in url:
            return
        

        # convert to relative url and change the lang folder
        relative_url = url.replace(portal_url, '').strip('/')
        default_url = '/'.join([default] + relative_url.split('/')[1:])

        try:
            default_obj = portal.restrictedTraverse(default_url)
        except (AttributeError, KeyError, TypeError):
            # the default version of the object was not found
            return

        return default_obj

    def get_fallback_url(self, url):
        """Get fallback url for a non-existing url so users can continue
        browsing the site. It tries to find an object in the same language
        by going up the hierarchy. If no object was found, it returns portal
        url.

        :param url: absolute url of the object that was not found
        :returns: url of an object that exists (in worst case portal url)
        """
        portal = self.context.portal_url.getPortalObject()
        portal_url = portal.absolute_url()
        if not url.startswith(portal_url):
            return

        if 'resolveuid' in url:
            return

        def _find_url(relative_url):
            try:
                obj = portal.restrictedTraverse(relative_url)
                return obj.absolute_url()
            except (AttributeError, KeyError, TypeError):
                #  parent url in this language wasn't found, return portal url
                if '/' not in relative_url:
                    return portal.absolute_url()

                # try moving up the hierarchy
                parent_url = '/'.join(relative_url.split('/')[:-1])
                return _find_url(parent_url)

        relative_url = url.replace(portal_url, '').strip('/')
        return _find_url(relative_url)
