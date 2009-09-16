from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from zope import component

def run(self):
    ltool = getToolByName(self, 'portal_languages')
    langs = ltool.listSupportedLanguages()
    langs.sort()
    paths = ['/osha/portal/%s/publications/factsheets' % lang[0] for lang in langs]
    paths += ['/osha/portal/%s/publications/e-facts' % lang[0] for lang in langs]
    files = self.portal_catalog(
                    portal_type='File',
                    created={'query': DateTime()-2, 'range':'min'}, 
                    sort_on='modified',
                    Language='all',
                    path=paths,
                    )

    l = []
    titles = []
    for f in files:
        try:
            obj = f.getObject()
        except:
            continue

        # if 'E-fact' in obj.Title() or 'Factsheet' in obj.Title():
        #     continue

        # l.append(obj.Title())
        # number = obj.getId().split('.')[0][-2:]
        # path = obj.absolute_url()
        # if 'factsheets' in path:
        #     title = 'Factsheet %s' % number
        # elif 'e-facts' in path:
        #     title = 'E-fact %s' % number
        # if obj.Title() != obj.getId():
        #     title = title + ' - ' + obj.Title()
        

        wf = self.portal.portal_workflow
        titles.append(wf.getInfoFor(obj, 'review_state'))

    return titles or 'None'

