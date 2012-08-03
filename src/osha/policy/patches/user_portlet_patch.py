from persistent.list import PersistentList
from plone.app.portlets.storage import UserPortletAssignmentMapping

def values(self):
    """ See `IOrderedContainer`.

    >>> oc = OrderedContainer()
    >>> oc.keys()
    []
    >>> oc['foo'] = 'bar'
    >>> oc.values()
    ['bar']
    >>> oc['baz'] = 'quux'
    >>> oc.values()
    ['bar', 'quux']
    >>> int(len(oc._order) == len(oc._data))
    1
    """
    res = list()
    failed = list()
    for item in self._order:
        try:
            res.append(self._data[item])
        except:
            failed.append(item)
    if len(failed) > 0:
        order = PersistentList()
        [order.append[x] for x in self._order if x not in failed]
        self._order = order
        self._p_changed = True
    return res

UserPortletAssignmentMapping.values = values
