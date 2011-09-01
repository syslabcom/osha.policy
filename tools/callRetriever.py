#!/usr/bin/env python

import os
import subprocess
import sys


# Optimise by making these options parameters passed in the command line
HOST = "http://localhost:8080/osha/portal/"
SCRIPT = "LCRetrieveURLs"
PATHSFILE = "PATHS"
SUCCESSFILE = "SUCCESS"
FAILEDFILE = "FAILED"
LINES_TO_READ = 500


def retrieve():
    data = open(PATHSFILE, 'r').read()
    lines = [x for x in data.split('\n') if x.strip() != '']
    if len(lines) == 0:
	print "FINISHED, no more paths left"
	return False
    paths, rest = lines[:LINES_TO_READ], lines[LINES_TO_READ:]

    # delete downloaded file, if it exists
    if os.path.exists(SCRIPT):
        os.remove(SCRIPT)

    URL = "%(host)s/%(script)s" % dict(host=HOST, script=SCRIPT)
    post_arg = ""
    for path in paths:
        post_arg += "&paths:list=%s" % path
    ret = subprocess.call(['wget', URL, '-U', 'Mozilla', '--post-data=%s' % post_arg])
    status = open(SCRIPT, 'r').read()
    statlines = status.split("\n")

    # all FAIL paths must be added again
    failed = list()
    success = list()
    for i in range(len(statlines)):
        line = statlines[i]
        k,v = line.split('#', 1)
        if i == 0:
            code = int(k)
            if code == -1:
                sys.exit(v)
        else:
            if k == "OK":
                success.append(v)
            elif k == "FAIL":
                failed.append(v)
            else:
                print "wtf? stupid status code: %s" % line

    # Now write out remaining paths file
    fh = open(PATHSFILE, 'w')
    fh.write('\n'.join(rest)+'\n')
    fh.close()
    # and the success and failed paths
    if len(success):
        fh = open(SUCCESSFILE, 'a')
        fh.write('\n'.join([x for x in success if x.strip() != ""])+'\n')
        fh.close()
    if len(failed):
        fh = open(FAILEDFILE, 'a')
        fh.write('\n'.join([x for x in failed if x.strip() != ""])+'\n')
	fh.close()



if __name__ == "__main__":
    loop = True
    while loop:
        result = retrieve()
	if result is not None:
	    loop = not not result

