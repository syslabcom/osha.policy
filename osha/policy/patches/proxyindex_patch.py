# Patch file
from Products.ProxyIndex.ProxyIndex import ProxyIndex, PROXIED_INDEX_ID
from Products.ProxyIndex.ProxyIndex import getIndexForType
from Products.ProxyIndex.Expression import Expression

from Products.ZCatalog.Catalog import CatalogSearchArgumentsMap

import zLOG
zLOG.LOG('elevateIT', 0, 'System Patch', detail="*** Patching __init__ of ProxyIndex ***")

def __init__patched(self, id, extra, caller=None):
    self.id = id

    extra['idx_caller'] = caller # save the caller for lexicon lookup
    idx_type = extra['idx_type']
    value_expr = extra['value_expr']
    
    extra['indexed_attrs']=''
    self._idx_type = idx_type
    self.idx  = getIndexForType(self, idx_type, extra)
    self._expr = Expression(value_expr)
    
    
def _apply_index_patched(self, request, cid=''):
    apply_index = self.getProxyAttribute('_apply_index')

    # implicit pluggable interface contract 
    if not request.has_key(self.id):
        return None
    else:
        advanced_query = 0
        # If request is a dictionary and not a CatalogSearchArgumentsMap,
        # the method was probably called by AdvancedQuery
        if isinstance(request, dict):
            request = CatalogSearchArgumentsMap(request, {})
            advanced_query = 1
        request.keywords[PROXIED_INDEX_ID]=request.get(self.id)
    
    res = apply_index(request, cid)
    # We obviously need to satisfy 2 different interfaces.
    # For AdvancedQuery, return only the list of results WITHOUT the PROXIED_INDEX_ID
    if advanced_query:
        return res[0], self.id
    else:
        return res
        
ProxyIndex.__init__ = __init__patched
ProxyIndex._apply_index = _apply_index_patched
