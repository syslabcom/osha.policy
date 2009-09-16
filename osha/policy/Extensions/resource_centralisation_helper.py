
def run(self):

    ltool = getToolByName(self, 'portal_languages')
    langs = ltool.listSupportedLanguages()
    langs.sort()
    paths = ['/osha/portal/%s/' % lang[0] for lang in langs]
    paths += ['/osha/portal/%s/' % lang[0] for lang in langs]

    ls = self.portal_catalog(
                    portal_type='News',
                    Language='all',
                    path=paths,
                    )

