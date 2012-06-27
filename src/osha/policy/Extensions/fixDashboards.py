from logging import getLogger
from Products.CMFCore.utils import getToolByName
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY, USER_CATEGORY
from zope.component import getUtility
from plone.portlets.interfaces import IPortletManager
import transaction

log = getLogger('fix dashboards')

def remove_dashboards(self):
    ptool = getToolByName(self, 'portal_url')
    portal = ptool.getPortalObject()
    dashboards = [
        getUtility(IPortletManager, name=name) for name in
        ['plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3',
         'plone.dashboard4']]

    for userid in portal.Members.objectIds('ATFolder'):
        print userid
        for dashboard in dashboards:
            try:
                dashmapping = assignment_mapping_from_key(
                    portal, dashboard.__name__, USER_CATEGORY, key=userid)
            except KeyError, e:
                msg = "Cannot find the portlet mapping for %s: %s" %(
                    userid, e)
                print msg
                log.info(msg)
                continue
            dashportlets = [x for x in dashmapping.keys()]
	    dashmapping._data.clear()
	    dashmapping._p_changed = True
	    dashmapping._data._p_changed = True
	transaction.commit()



