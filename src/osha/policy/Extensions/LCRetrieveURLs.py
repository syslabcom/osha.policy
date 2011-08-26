""" Extract the paths passed in the REQUEST, fetch the objects, and
    retrieve them.
    Return a status indicator for every path
"""

from Products.CMFCore.utils import getToolByName
from time import time

def retrieve(self):
    start = time()
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
            status.append("FAIL#%s#%s" % (err, path))
            continue
        try:
            lc.retrieving.retrieveObject(ob, online=False)
            status.append("OK#%s" % path)
        except Exception, err:
            status.append("FAIL#%s#%s" % (err,path))
    finished = time()
    delta = finished - start
    msg = "%d#Paths were processed. Time: %2.2fs \n" % (len(paths), delta)
    msg += "\n".join(status)

    return msg

