# Ticket #3204 - potential speed improvements
# google page speed tool recommends at least 7 days of caching for resource files. 
# Default is 7, so google complains.
# We increase the value to 14

from Products.ResourceRegistries import config

config.CSS_CACHE_DURATION = 14  # css cache life in days (note: value can be a float)
config.KSS_CACHE_DURATION = 14  # kss cache life in days (note: value can be a float)
config.JS_CACHE_DURATION = 14   # js cache life in days (note: value can be a float)
