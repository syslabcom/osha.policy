from Acquisition import aq_base
from DateTime import DateTime
from Products.CMFPlone import utils as cmfutils
from Products.Collage.interfaces import IDynamicViewManager
from Products.Collage.utilities import findFirstAvailableInteger
from Products.Collage.utilities import generateNewId
from slc.publications.interfaces import IPublicationEnhanced

from urlparse import urljoin


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


def createOshMail(
        self,
        id="",
        title="",
        formname="",
        year='',
        month='',
        day='',
        nocontent=False):

    if not id:
        msg = "You did not give an ID."
        self.plone_utils.addPortalMessage(msg)
        return self.REQUEST.RESPONSE.redirect(formname)

    if hasattr(aq_base(self), id):
        msg = "The ID '%s' is already in use!" % id
        self.plone_utils.addPortalMessage(msg)
        return self.REQUEST.RESPONSE.redirect(formname)

    ### Begin Framework

    self.invokeFactory(id=id, type_name='Collage')
    om = getattr(self, id)
    om.unmarkCreationFlag()
    om.setTitle(title)

    row1, col1_1 = insertRow(om)
    col1_2 = splitColumn(row1)
    manager = IDynamicViewManager(row1)
    manager.setLayout('large-left')

    pc = self.portal_catalog

    def addToOshmail(path="", layout="", column=None):
        abspath = urljoin(portal_path(self), path)
        uid = getUIDForPath(pc, abspath)
        if uid:
            alias = insertAlias(column, uid)
            manager = IDynamicViewManager(alias)
            manager.setLayout(layout)

    def addToLeftCol(path=""):
        addToOshmail(path=path, layout="oshmail", column=col1_1)

    def addToRightCol(path="", layout=""):
        addToOshmail(path=path, layout=layout, column=col1_2)

    def addMultipleToOshmail(
            items=None, column=None, max=0, layout="", offset=0):
        for ob in items[:max]:
            alias = insertAlias(column, ob.UID)
            manager = IDynamicViewManager(alias)
            manager.setLayout(layout)
            for count in range(offset):
                column.moveObjectsUp(alias.id)
            cmfutils.getToolByName(
                self, 'plone_utils').reindexOnReorder(column)

    def addMultipleToLeftCol(items=None, max=0, layout="oshmail", offset=0):
        addMultipleToOshmail(
            items=items, column=col1_1, max=max, layout=layout, offset=offset)

    def addMultipleToRightCol(
            items=None, max=0, layout="right_column", offset=0):
        addMultipleToOshmail(
            items=items, column=col1_2, max=max, layout=layout, offset=offset)

    # The 2-column lay-out is now merged into ONE row to have greatest
    # possible flexibility for the right column.
    # The lay-out is now:
    # Highlights     || Blog
    # Did you know   || News
    # Site in focus  || Events
    # Campaign News  ||
    # Press releases ||
    # Publications   ||
    # Coming soon    ||

    # Headings, editable and translated portal content
    addToRightCol(path="en/news/oshmail/blog")
    addToRightCol(path="en/news/oshmail/view-the-blog", layout="clickable")
    addToRightCol(path="en/news/oshmail/news")
    addToRightCol(path="en/news/oshmail/more-news", layout="clickable")
    addToRightCol(path="en/news/oshmail/events")
    addToRightCol(path="en/news/oshmail/more-events", layout="clickable")

    addToLeftCol(path="en/news/oshmail/highlights")
    addToLeftCol(path="en/news/oshmail/osh-matters")
    addToLeftCol(path="en/news/oshmail/read-our-latest-publications")
    addToLeftCol(path="en/news/oshmail/coming-soon")

    ## END Framework

    ## Begin Content
    if nocontent:
        msg = "Collage template was successfully created"
    else:
        msg = "Collage template including content was successfully created"

        now = DateTime()
        try:
            valid_from = DateTime('%s/%s/%s' % (year, month, day))
        except:
            valid_from = now - 30

        query = {
            'Language': ['', 'en'],
            'review_state': 'published',
            'sort_limit': 15,
            'sort_on': 'effective',
        }

        blog_query = dict(
            portal_type=['Blog Entry'],
            sort_order='reverse',
        )
        latest_blog_entry = pc(dict(query.items() + blog_query.items()))
        addMultipleToRightCol(items=latest_blog_entry, max=1, offset=5)

        news_query = {
            'effective': {'query': valid_from, 'range': 'min'},
            'expires': {'query': now, 'range': 'min'},
            'path': {'query': '/osha/portal/en/news', 'depth': 1},
            'portal_type': ('News Item',),
            'sort_order': 'reverse',
        }
        news = pc(dict(query.items() + news_query.items()))
        addMultipleToRightCol(items=news, max=15, offset=3)

        events_query = {
            'portal_type': ['Event', 'SPSeminar'],
            'path': dict(
                query=['/osha/portal/en/events', '/osha/portal/en/seminars'],
                depth=-1),
            'end': {'query': now, 'range': 'min'},
            'sort_on': 'start',
        }
        events = pc(dict(query.items() + events_query.items()))
        addMultipleToRightCol(
            items=events, max=15, layout="standard", offset=1)

        highlights_query = {
            'path': ['/osha/portal/en/teaser'],
            'sort_limit': 2,
        }
        highlights = pc(
            dict(query.items() + news_query.items() + highlights_query.items())
        )
        addMultipleToLeftCol(
            items=highlights, max=2, layout="standard", offset=3)

        # osh_matters ?

        publications_query = {
            'object_provides': IPublicationEnhanced.__identifier__,
            'path': dict(query='/osha/portal/en/publications', depth=-1),
            'effective': dict(query=(valid_from, now), range='min:max'),
            'sort_limit': 5,
        }
        publications = pc(dict(query.items() + publications_query.items()))
        addMultipleToLeftCol(items=publications, max=5, layout="oshmail_title", offset=1)

        # coming_soon ?
    om.reindexObject()
    self.plone_utils.addPortalMessage(msg)
    return self.REQUEST.RESPONSE.redirect(om.absolute_url())
