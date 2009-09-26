from zope.interface import directlyProvides
from zope import component
import zope.thread
import plone.memoize.ram
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.ram import MemcacheAdapter
import os
import memcache

thread_local = zope.thread.local()

def choose_cache(fun_name):
    global servers
    client=getattr(thread_local, "client", None)
    if client is None:
        servers=os.environ.get(
            "MEMCACHE_SERVER", "127.0.0.1:11211").split(",")
        client=thread_local.client=memcache.Client(servers, debug=0)

    return MemcacheAdapter(client, globalkey='osha')

directlyProvides(choose_cache, ICacheChooser)

