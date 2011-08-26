#!/usr/bin/env python

import os
import subprocess
import sys


# Optimise by making these options parameters passed in the command line
HOST = "http://localhost:8080/gfb/"
SCRIPT = "LCRetrieveURLs"
PATHSFILE = "PATHS"
LINES_TO_READ = 2


def retrieve():
    # delete downloaded file, if it exists
    if os.path.exists(SCRIPT):
        os.remove(SCRIPT)

    data = open(PATHSFILE, 'r').read()
    lines = data.split('\n')
    paths, rest = lines[:LINES_TO_READ], lines[LINES_TO_READ:]
    
    URL = "%(host)s/%(script)s" % dict(host=HOST, script=SCRIPT)
    post_arg = ""
    for path in paths:
        post_arg += "&paths:list=%s" % path
    ret = subprocess.call(['wget', URL, '-U', 'Mozilla', '--post-data=%s' % post_arg])
    status = open(SCRIPT, 'r').read()
    statlines = status.split("\n")

    # all FAIL paths must be added again
    failed = list()
    for i in range(len(statlines)):
        line = statlines[i]
        k,v = line.split('#', 1)
        if i == 0:
            code = int(k)
            if code == -1:
                sys.exit(v)
        else:
            if k == "OK":
                print "yeah, %s was good" % v
            elif k == "FAIL":
                print "damm, %s was bad" % v
                failed.append(v)
            else:
                print "wtf? stupid status code: %s" % line

    # Now write out remaining paths file
    fh = open(PATHSFILE, 'w')
    new_paths = [x for x in (rest + failed) if x.strip() != ""]
    fh.write("\n".join(new_paths))
    fh.close()


if __name__ == "__main__":
    retrieve()
