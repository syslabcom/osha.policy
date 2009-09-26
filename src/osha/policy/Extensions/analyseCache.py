RES = []
def log(txt):
    RES.append(txt)

def analyseCache(self):
    db = self._p_jar.db()
    detail = db.cacheExtremeDetail()
    SIZE = []
    for i in detail:
        oid = i['oid']
        ob = self._p_jar.get(oid)
        if ob is None:
            continue
        if hasattr(ob, 'get_size'):
            try:
                id = ob.id or oid
                if callable(id):
                    id = id()
                SIZE.append((ob.get_size(), oid, id))
            except Exception, e:
                log("GetSize Excepted on %s: %s" % (oid, str(e)) )
    SIZE.sort()
    SIZE.reverse()
    total = 0
    for i in SIZE:
        total += i[0]
    #import pdb;pdb.set_trace()
    
    return "Total:"+str(total)+"\n\n" + "\n".join(["%s:: %s - %s" % x for x in SIZE[:500]]) 
    #+ "\n".join(RES)
    