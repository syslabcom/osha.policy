from zope import component
from Products.CMFCore.utils import getToolByName
from p4a.subtyper.interfaces import ISubtyper


annotated_link_subtyped = \
['http://tdeimos1:5040/osha/portal/sub/napo/en/home',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/liechtenstein/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/lithuania/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/malta/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/portugal/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/poland/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/netherlands/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/croatia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/the-former-yugoslav-republic-of-macedonia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/latvia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/czech-republic/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/ireland/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/denmark/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/austria/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/hungary/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/estonia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/switzerland/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/norway/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/bosnia-and-herzegovina/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/serbia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/iceland/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/cyprus/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/belgium/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/romania/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/france/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/greece/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/finland/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/sweden/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/montenegro/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/albania/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/slovenia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/united-kingdom/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/spain/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/slovakia/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/germany/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/turkey/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/luxembourg/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/italy/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/kosovo-under-unscr-1244-99/index_html',
'http://tdeimos1:5040/osha/portal/en/oshnetwork/member-states/bulgaria/index_html']


def run(self):
    obs = []
    duds = []
    subtyper = component.getUtility(ISubtyper)
    documents = self.portal_catalog(portal_type='Document')
    for doc in documents:
        type = None
        try:
            doc = doc.getObject()
        except:
            duds.append(doc.getPath())
            continue

        type = subtyper.existing_type(doc)
        if type:
            if type.name == 'annotatedlinks':
                obs.append(doc.absolute_url())
                subtyper.remove_type(doc)
                subtyper.change_type(doc, 'annotatedlinks')

    return obs

