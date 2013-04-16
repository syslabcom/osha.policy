from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage


class AlignLanguages(BrowserView):
    """ Sets the languages of a folder's contents to be the same as the
        folder's language. By default only sets File objects, this can be
        changed by the request parameter portal_type, where an empty value
        means all types.
    """
    def __call__(self):
        portal_type = self.request.get('portal_type', ['File', ])
        status = IStatusMessage(self.request)
        cnt = 0
        lang = self.context.Language()
        for subobj in self.context.objectValues():
            if not portal_type or subobj.portal_type in portal_type:
                if subobj.Language() != lang:
                    subobj.setLanguage(lang)
                    cnt += 1

        if cnt > 0:
            msg = 'Align content languages handled a total of %d items of ' \
                'type %s.' % (cnt, ', '.join(portal_type))
        else:
            msg = 'Align content languages: nothing needed to be done for '\
                'items of type %s.' % ', '.join(portal_type)
        status.addStatusMessage(msg, type='info')
        self.request.RESPONSE.redirect(self.context.absolute_url())
