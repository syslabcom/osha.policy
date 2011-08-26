""" Extract the paths passed in the REQUEST, fetch the objects, and
    retrieve them.
    Return a status indicator for every path
"""

from Products.CMFCore.utils import getToolByName

def retrieve(self):
    paths = self.REQUEST.get('paths', list())
    if len(paths) == 0:
        return "-1#No paths were passed"

    lc = getToolByName(self, 'portal_linkchecker')
    try:
        server = lc.database._getWebServiceConnection()
    except Exception, err:
        return "-1#Not connected to LMS"
    status = list()
    for path in paths:
        try:
            ob = self.unrestrictedTraverse(path)
        except Exception, err:
            status.append("FAIL#%s" % path)
            continue
        try:
            lc.retrieving.retrieveObject(ob, online=False)
            status.append("OK#%s" % path)
        except Exception, err:
            status.append("FAIL#%s" % path)
    msg = "%d#Paths were processed\n" % len(paths)
    msg += "\n".join(status)
    return msg

