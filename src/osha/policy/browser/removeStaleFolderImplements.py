# -*- coding: utf-8 -*-

import transaction
from Products.Five.browser import BrowserView

import logging
log = logging.getLogger('osha.policy')


class RemoveImplementsView(BrowserView):

    def __call__(self):
        log.info("Remove stale interface from folders")
        global cnt, skipped

        includeTranslations = self.request.get('includeTranslations', False)
        if isinstance(includeTranslations, basestring):
            includeTranslations = (includeTranslations.lower() == 'true')

        cnt = skipped = 0

        def handleItems(items):
            global cnt, skipped
            for item in items:
                id, obj = item

                if includeTranslations and obj.getCanonical():
                    translations = map(lambda t: t[0], obj.getTranslations().values())
                else:
                    translations = [obj]

                for trans in translations:
                    if trans.__implemented__.__name__.endswith('?'):
                        del trans.__implemented__
                        cnt += 1
                    else:
                        skipped += 1
                    if cnt > 0 and cnt % 1000 == 0:
                        log.info("Commit after %d" % cnt)
                        transaction.commit()

        res = self.context.ZopeFind(self.context, obj_metatypes=['ATFolder'], search_sub=1)
        res = [(self.context.getId(), self.context)] + res
        handleItems(res)
        status = "Handled a total of %(cnt)d items and skipped %(skipped)d. " \
            "Translations were %(transl)s" % dict(cnt=cnt,
            skipped=skipped,
            transl=(includeTranslations and 'handled' or 'ignored'))
        log.info(status)
        return status
