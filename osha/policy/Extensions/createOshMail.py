from Products.Collage.utilities import generateNewId, findFirstAvailableInteger
from Products.Collage.interfaces import ICollageBrowserLayer, IDynamicViewManager
from urlparse import urljoin
from Acquisition import aq_base
from DateTime import DateTime
from slc.publications.interfaces import IPublicationEnhanced

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

def createOshMail(self, id="", title="", formname="", year='', month='', day=''):
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
    
    # row 1 (teaser // news)
    row1, col1_1 = insertRow(om)
    col1_2 = splitColumn(row1)
    manager = IDynamicViewManager(row1)
    manager.setLayout('large-left')
    path = "en/news/oshmail/latest-news"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1_1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')
    
    path = "en/news/oshmail/news"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1_2, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('right_column')
    
    # row 2 (highlights, did you know // events)
    row2, col2_1 = insertRow(om)
    col2_2 = splitColumn(row2)
    manager = IDynamicViewManager(row2)
    manager.setLayout('large-left')
    path = "en/news/oshmail/highlights"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col2_1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')
    
    path = "en/news/oshmail/did-you-know"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col2_1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')
    
    path = "en/news/oshmail/events"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col2_2, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('right_column')
    
    
    # row 3 (site in focus // nothing)
    row3, col3_1 = insertRow(om)
    col3_2 = splitColumn(row3)
    manager = IDynamicViewManager(row3)
    manager.setLayout('large-left')
    path = "en/news/oshmail/site-in-focus"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col3_1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')
    
    
    # row 4 (Press releases // nothing)
    row4, col4_1 = insertRow(om)
    col4_2 = splitColumn(row4)
    manager = IDynamicViewManager(row4)
    manager.setLayout('large-left')
    path = "en/news/oshmail/read-our-latest-press-releases"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col4_1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')
    
    
    # row 5 (Publications // nothing)
    row5, col5_1 = insertRow(om)
    col5_2 = splitColumn(row5)
    manager = IDynamicViewManager(row5)
    manager.setLayout('large-left')
    path = "en/news/oshmail/read-our-latest-publications"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col5_1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')
    
    # row 6 (tell a friend)
    row6, col6_1 = insertRow(om)
    path = "en/news/oshmail/tellafriend"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col6_1, uid)
    
    ## END Framework

    ## Begin Content
    now = DateTime()
    try:
        valid_from = DateTime('%s/%s/%s' %(year, month, day))
    except:
        valid_from = now-30

    
    # teasers
    query = {'path': {'query': ['/osha/portal/en/teaser'], 'depth': 1}, 
        'sort_on': 'effective', 'sort_order': 'reverse', 'portal_type': 'News Item',
        'effective': {'query': now, 'range': 'max'},
        'expires': {'query': now, 'range': 'min'},
        'Language': ('en', '')}
    teasers = pc(query)
    for ob in teasers[:5]:
        alias = insertAlias(col1_1, ob.UID)
    
    # news
    query = {'sort_on': 'effective', 'sort_order': 'reverse',
        'effective': {'query': now, 'range': 'max'}, 
        'expires': {'query': now, 'range': 'min'},  
        'path': {'query': '/osha/portal/en/news', 'depth': 1}, 
        'review_state': 'published', 
        'portal_type': ('News Item',),
        'sort_limit': 5}
    news = pc(query)
    for ob in news[:5]:
        alias = insertAlias(col1_2, ob.UID)
        manager = IDynamicViewManager(alias)
        manager.setLayout('right_column')
        
    
    # events

    query = dict(portal_type=['Event','SPSeminar'],
                       review_state='published',
                       path=dict(query='/osha/portal/en', depth=-1),
                       end={'query': now, 'range': 'min'},
                       sort_on='start',
                       Language=['', 'en'],
                       sort_limit=5)
    events = pc(query)
    for ob in events[:5]:
        alias = insertAlias(col2_2, ob.UID)

    # press releases

    query = dict(portal_type='PressRelease',
                       review_state='published',
                       path=dict(query='/osha/portal/en/press', depth=-1),
                       sort_on='effective',
                       Language=['', 'en'],
                       created=dict(query=(valid_from, now), range='min:max'),
                       sort_limit=5)
    pressreleases = pc(query)
    for ob in pressreleases[:5]:
        alias = insertAlias(col4_1, ob.UID)
        manager = IDynamicViewManager(alias)
        manager.setLayout('right_column')     

    # publications

    query = dict(object_provides='slc.publications.interfaces.IPublicationEnhanced',
                       review_state='published',
                       path=dict(query='/osha/portal/en/publications', depth=-1),
                       sort_on='effective',
                       Language=['', 'en'],
                       created=dict(query=(valid_from, now), range='min:max'),
                       sort_limit=5)
    publications = pc(query)
    for ob in publications[:5]:
        alias = insertAlias(col5_1, ob.UID)


    om.reindexObject()
    msg = "Collage template was successfully created"
    self.plone_utils.addPortalMessage(msg)
    return self.REQUEST.RESPONSE.redirect(om.absolute_url())