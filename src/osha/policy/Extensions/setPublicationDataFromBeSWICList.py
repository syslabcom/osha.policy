from Products.CMFCore.utils import getToolByName
import os
from DateTime import DateTime

SEPARATOR = '\t'

ID = 0
NR = 1
DATE = 2
TITLE_NL = 3
TITLE_FR = 4
DESCR_NL = 5
DESCR_FR = 6
PATH_NL = 7
PATH_FR = 8

def doit(self, path_to_file=""):
    print "\n\n\nsetPublicationData from BeSWIC list"
    if not path_to_file:
        return "please supply path_to_file that contains the necessary data"
    if not os.access(path_to_file, os.F_OK):
        return "Could not open file at %s" % path_to_file
    fh = open(path_to_file, 'r')
    data = fh.read()
    fh.close()
    lines = data.split('\n')
    print "nr of lines:", len(lines)
    headers = lines[0].split(SEPARATOR)
    numitems = len(headers)
    print headers, numitems
    i = 2
    for line in lines[1:]:
        if not line.strip():
            continue
        items = line.split(SEPARATOR)
        if len(items)!=numitems:
            print "ERROR wrong number of items:"
            print i, items

        
        parts = items[NR].split(" ")
        parts = [x for x in parts if x.strip()!='-']
        try:
            loc_nl, loc_fr = parts[-1].split('/')
            rest = " ".join(parts[:-1])
        except:
            try:
                #import pdb; pdb.set_trace()
                if len(parts)>=4:
                    if parts[-2]=='/':
                        loc_nl = parts[-3]
                        loc_fr = parts[-1]
                        rest = " ".join(parts[:-3])
                    else:
                        raise
                else:
                    raise
            except:
                loc_nl = loc_fr = ""
                rest = "EXTRACTING TITLE NOT POSSIBLE - PLEASE CORRECT MANUALLY"
                print "error in line", i
    
        title_nl = "%s %s: %s" %(rest, loc_nl, items[TITLE_NL])
        title_nl = unicode(title_nl, 'utf-8')
        title_fr = "%s %s: %s" %(rest, loc_fr, items[TITLE_FR])
        title_fr = unicode(title_fr, 'utf-8')
        
        try:
            date = DateTime(items[DATE], datefmt="international")
        except:
            date = None
        
        descr_nl = "%s - Vraag gesteld door " %items[DESCR_NL]
        descr_fr = "%s - Question posé par " %items[DESCR_FR]
        i+=1
    
    return "done - no problems"