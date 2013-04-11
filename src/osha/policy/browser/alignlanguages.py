from Products.Five import BrowserView


class AlignLanguages(BrowserView):
    """ Sets the languages of a folder's contents to be the same as the
        folder's language. By default only sets File objects, this can be
        changed by the request parameter portal_type, where an empty value
        means all types.
    """
    def __call__(self):
        portal_type = self.request.get('portal_type', ['File', ])
        lang = self.context.Language()
        for subobj in self.context.objectValues():
            if not portal_type or subobj.portal_type in portal_type:
                subobj.setLanguage(lang)
        self.request.RESPONSE.redirect(self.context.absolute_url())
