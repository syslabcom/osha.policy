from plone.app.portlets.portlets.portletcontext import ContentContext
from Products.CMFCore.utils import getToolByName
from types import StringTypes

def _getGroupIds(self):
    membership = getToolByName(self.context, 'portal_membership', None)
    if membership is None or membership.isAnonymousUser():
        return ()

    member = membership.getAuthenticatedMember()
    if not member:
        return ()
    if hasattr(member, 'getGroups'):
        groups = member.getGroups()
    else:
        groups = []
        
    # Ensure we get the list of ids - getGroups() suffers some acquision
    # ambiguity - the Plone member-data version returns ids.

    for group in groups:
        if type(group) not in StringTypes:
            return ()

    return sorted(groups)

ContentContext._getGroupIds = _getGroupIds
