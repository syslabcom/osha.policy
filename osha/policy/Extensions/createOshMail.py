from Products.Collage.utilities import generateNewId, findFirstAvailableInteger
from Products.Collage.interfaces import ICollageBrowserLayer, IDynamicViewManager
from urlparse import urljoin
from Acquisition import aq_base

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

def createOshMail(self, id="om98", title="Oshmail 98 - 2008", formname=""):
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
    print om

    # row 1 (teaser // news)
    row1, col1 = insertRow(om)
    col2 = splitColumn(row1)
    manager = IDynamicViewManager(row1)
    manager.setLayout('large-left')
    path = "en/news/oshmail/latest-news"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')

    path = "en/news/oshmail/news"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col2, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('right_column')

    # row 2 (highlights, did you know, site in focus // events)
    row2, col1 = insertRow(om)
    col2 = splitColumn(row2)
    manager = IDynamicViewManager(row2)
    manager.setLayout('large-left')
    path = "en/news/oshmail/highlights"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')

    path = "en/news/oshmail/did-you-know"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')

    path = "en/news/oshmail/site-in-focus"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')    

    path = "en/news/oshmail/events"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col2, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('right_column')

    # row 3 (Press releases // nothing)
    row3, col1 = insertRow(om)
    col2 = splitColumn(row3)
    manager = IDynamicViewManager(row3)
    manager.setLayout('large-left')
    path = "en/news/oshmail/read-our-latest-press-releases"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')

    # row 4 (Publications // nothing)
    row4, col1 = insertRow(om)
    col2 = splitColumn(row4)
    manager = IDynamicViewManager(row4)
    manager.setLayout('large-left')
    path = "en/news/oshmail/read-our-latest-publications"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)
    manager = IDynamicViewManager(alias)
    manager.setLayout('oshmail')

    # row 5 (tell a friend)
    row5, col1 = insertRow(om)
    path = "en/news/oshmail/tellafriend"
    abspath = urljoin(portal_path(self), path)
    uid = getUIDForPath(pc, abspath)
    alias = insertAlias(col1, uid)

    msg = "Collage template was successfully created"
    self.plone_utils.addPortalMessage(msg)
    return self.REQUEST.RESPONSE.redirect(om.absolute_url())