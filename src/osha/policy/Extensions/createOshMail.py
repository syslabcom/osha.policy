from Products.Collage.utilities import generateNewId, findFirstAvailableInteger
from Products.Collage.interfaces import ICollageBrowserLayer, IDynamicViewManager
from urlparse import urljoin
from Acquisition import aq_base
from DateTime import DateTime
from slc.publications.interfaces import IPublicationEnhanced
from Products.CMFPlone import utils as cmfutils

def insertRow(collage):
    desired_id = generateNewId(collage)
    row_id = collage.invokeFactory(id=desired_id, type_name='CollageRow')
    row = getattr(collage, row_id, None)
    row.setTitle('')

    # create column
    desired_id = generateNewId(row)
    col_id = row.invokeFactory(id=desired_id, type_name='CollageColumn')
    col = getattr(row, col_id, None)
    col.setTitle('')

    return row, col


def splitColumn(row):
    desired_id = generateNewId(row)
    col_id = row.invokeFactory(id=desired_id, type_name='CollageColumn')
    col = getattr(row, col_id, None)
    return col

def insertAlias(col, uid):
    prefix = 'alias-'
    ids = [i[6:] for i in col.objectIds() if i.startswith('alias-')]
    alias_id = 'alias-%s' % findFirstAvailableInteger(ids)
    # create new alias
    col.invokeFactory('CollageAlias', id=alias_id)
    alias = col[alias_id]
    # set target
    alias.set_target(uid)
    return alias


def getUIDForPath(cat, path):
    res = cat(path=path)
    if len(res):
        return res[0].getObject().UID()
    return ""

def portal_path(self):
    url_tool = self.portal_url
    return '/'.join(url_tool.getPortalObject().getPhysicalPath() + ('',))

def createOshMail(self, id="", title="", formname="", year='', month='', day='', nocontent=False):
    pc = self.portal_catalog

    if not id:
        msg = "You did not give an ID."
        self.plone_utils.addPortalMessage(msg)
        return self.REQUEST.RESPONSE.redirect(formname)

    if hasattr(aq_base(self), id):
        msg = "The ID '%s' is already in use!" %id
        self.plone_utils.addPortalMessage(msg)
        return self.REQUEST.RESPONSE.redirect(formname)
    self.invokeFactory(id=id, type_name='Collage')
    om = getattr(self, id)
    om.unmarkCreationFlag()
    om.setTitle(title)
    
    ### Begin Framework
    #
    # The 2-column lay-out is now merged into ONE row to have greatest
    # possible flexibility for the right column.
    # The lay-out is now:
    # Highlights     || Social Media
    # Did you know   || News
    # Site in focus  || Events
    # Campaign News  ||
    # Press releases ||
    # Publications   ||
    # Coming soon    ||
    
    # row 1
    row1, col1_1 = insertRow(om)
    col1_2 = splitColumn(row1)
    manager = IDynamicViewManager(row1)
    manager.setLayout('large-left')

    # Right column
    # Social media
    path = "en/news/oshmail/social-media"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:

        alias = insertAlias(col1_2, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('text')

    # News
    path = "en/news/oshmail/news"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_2, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('right_column')

    # Events
    path = "en/news/oshmail/events"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_2, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('right_column')

    # Blog
    path = "en/news/oshmail/blog"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_2, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('right_column')

    # Left column
    # Highlights
    path = "en/news/oshmail/highlights"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')

    # Did you know
    path = "en/news/oshmail/did-you-know"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')

    # Site in focus
    path = "en/news/oshmail/site-in-focus"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')

    # Campaign News
    path = "en/news/oshmail/campaign-news"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')

    # Press releases
    path = "en/news/oshmail/read-our-latest-press-releases"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')

    # Publications
    path = "en/news/oshmail/read-our-latest-publications"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')

    # Coming soon
    path = "en/news/oshmail/coming-soon"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col1_1, uid)
        manager = IDynamicViewManager(alias)
        manager.setLayout('oshmail')


    # row 6 (subscription info, tell a friend)
    row6, col6_1 = insertRow(om)
    path = "en/news/oshmail/more-oshmail"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col6_1, uid)
    path = "en/news/oshmail/subscription-information"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col6_1, uid)
    path = "en/news/oshmail/tellafriend"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    if uid:
        alias = insertAlias(col6_1, uid)

    ## END Framework

    ## Begin Content
    
    if not nocontent:
        now = DateTime()
        try:
            valid_from = DateTime('%s/%s/%s' %(year, month, day))
        except:
            valid_from = now-30


#        # teasers
#        query = {'path': {'query': ['/osha/portal/en/teaser'], 'depth': 1}, 
#            'sort_on': 'effective', 'portal_type': 'News Item',
#            'effective': {'query': now, 'range': 'max'},
#            'expires': {'query': now, 'range': 'min'},
#            'Language': ('en', ''),
#            'sort_limit': 5}
#        teasers = pc(query)
#        for ob in teasers[:5]:
#            alias = insertAlias(col1_1, ob.UID)

        # news
        query = {'sort_on': 'effective',
            'sort_order': 'reverse',
            'effective': {'query': valid_from, 'range': 'min'}, 
            'expires': {'query': now, 'range': 'min'},  
            'path': {'query': '/osha/portal/en/news', 'depth': 1}, 
            'review_state': 'published', 
            'portal_type': ('News Item',),
            'sort_limit': 15}
        news = pc(query)
        for ob in news[:15]:
            alias = insertAlias(col1_2, ob.UID)
            manager = IDynamicViewManager(alias)
            manager.setLayout('right_column')
            col1_2.moveObjectsUp(alias.id)
            cmfutils.getToolByName(self, 'plone_utils').reindexOnReorder(col1_2)

        # events

        query = dict(portal_type=['Event','SPSeminar'],
                           review_state='published',
                           path=dict(query='/osha/portal/en', depth=-1),
                           end={'query': now, 'range': 'min'},
                           sort_on='start',
                           Language=['', 'en'],
                           sort_limit=15)
        events = pc(query)
        for ob in events[:15]:
            alias = insertAlias(col1_2, ob.UID)
            col1_2.moveObjectsUp(alias.id)
            cmfutils.getToolByName(self, 'plone_utils').reindexOnReorder(col1_2)

#        # press releases
#
#        query = dict(portal_type='PressRelease',
#                           review_state='published',
#                           path=dict(query='/osha/portal/en/press', depth=-1),
#                           sort_on='effective',
#                           Language=['', 'en'],
#                           created=dict(query=(valid_from, now), range='min:max'),
#                           sort_limit=5)
#        pressreleases = pc(query)
#
#        for ob in pressreleases[:5]:
#            alias = insertAlias(col1_1, ob.UID)
#            manager = IDynamicViewManager(alias)
#            manager.setLayout('right_column')
#            col1_1.moveObjectsUp(alias.id)
#            cmfutils.getToolByName(self, 'plone_utils').reindexOnReorder(col1_1)
#
#        # publications
#
#        query = dict(object_provides='slc.publications.interfaces.IPublicationEnhanced',
#                           review_state='published',
#                           path=dict(query='/osha/portal/en/publications', depth=-1),
#                           sort_on='effective',
#                           Language=['', 'en'],
#                           created=dict(query=(valid_from, now), range='min:max'),
#                           sort_limit=5)
#        publications = pc(query)
#        for ob in publications[:5]:
#            alias = insertAlias(col1_1, ob.UID)
        
        msg = "Collage template including content was successfully created"
    else:
        msg = "Collage template was successfully created"


    # Add the most recent blog entry to the Highlights section
    query = dict(
        portal_type=['Blog Entry'],
        review_state='published',
        sort_on='effective',
        sort_order='reverse',
        Language=['', 'en'],
    )
    latest_blog_entry = pc(query)[0]
    alias = insertAlias(col1_2, latest_blog_entry.UID)
    manager = IDynamicViewManager(alias)
    manager.setLayout('right_column')

    om.reindexObject()
    self.plone_utils.addPortalMessage(msg)
    return self.REQUEST.RESPONSE.redirect(om.absolute_url())
