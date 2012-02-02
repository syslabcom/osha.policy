#!/usr/bin/env python

"""This little script is actually useful for the extranet.
I just save it here in order not to keep track of it"""


import os
import subprocess
import sys
import time

stale = [
    'bb3f3ae15f4ea8d7a939ebdc226bc237']

template = 'wget ""'
SCRIPT = "update"
URL = "http://localhost:8983/solr/update"
post_template = "stream.body=<delete><id>%s</id></delete>"

for id in stale:
    # delete downloaded file, if it exists
    if os.path.exists(SCRIPT):
        os.remove(SCRIPT)
    post_arg = post_template % id
    ret = subprocess.call(['wget', URL, '-U', 'Mozilla', '--post-data=%s' % post_arg])
    print ret
    time.sleep(1)

sys.exit('finished')
