from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import ILocalPortletAssignmentManager
from plone.portlets.constants import CONTEXT_CATEGORY
from plone.app.portlets.utils import assignment_mapping_from_key

# right = assignment_mapping_from_key(
#     obj, 'plone.rightcolumn', CONTEXT_CATEGORY, path
#     )

# portlets = [x for x in list(right.keys())]
# if old_portlet in portlets:
#     del right[old_portlet]

def main(self, REQUEST=None):
    names = [x[0] for x in zope.component.getUtilitiesFor(IPortletManager)]
    # filter out dashboard stuff
    names = [x for x in names if not x.startswith('plone.dashboard')]
    return names
