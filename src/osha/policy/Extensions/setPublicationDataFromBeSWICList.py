from Products.CMFCore.utils import getToolByName
import os
from DateTime import DateTime

SEPARATOR = '\t'
LANGUAGES = ['fr', 'nl']

ID = 0
NR = 1
DATE = 2
TITLE_NL = 3
TITLE_FR = 4
DESCR_NL = 5
DESCR_FR = 6
PATH_NL = 7
PATH_FR = 8


def split_filename(filename, languages):
    """ 
    Split the filename into its language, name and extension components.
    """

    if '.' in filename:
        file_id, file_ext = filename.rsplit('.', 1)
    else:
        file_id = filename
        file_ext = ''

    lang = ''

    l = file_id.split('_')
    if len(l[-1]) == 2 and l[-1] in languages:
        lang = l[-1]
        name = '_'.join(l[:-1])
    elif file_id.startswith('vraag'):
        lang = 'nl'
        name = file_id[5:]
    elif file_id.startswith('ques_'):
        lang = 'fr'
        name = file_id[5:]
    elif file_id.startswith('ques'):
        lang = 'fr'
        name = file_id[4:]

    if lang == '' or lang not in languages:
        return '', file_id, file_ext

    return lang, name, file_ext


def parseData(data):
    lines = data.split('\n')
    print "nr of lines:", len(lines)
    headers = lines[0].split(SEPARATOR)
    numitems = len(headers)
    print headers, numitems
    
    dataByFilename = dict()
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
        fname_nl = items[PATH_NL].split('/')[-1].lower()
        fname_fr = items[PATH_FR].split('/')[-1].lower()
        
        lang_nl, base_filename_nl, file_ext_nl =  split_filename(fname_nl, LANGUAGES)
        lang_fr, base_filename_fr, file_ext_fr =  split_filename(fname_fr, LANGUAGES)
        if base_filename_nl != base_filename_fr:
                print "%d: %s - %s (%s), %s - %s (%s)" %(i, base_filename_nl, fname_nl, lang_nl, base_filename_fr, fname_fr, lang_fr)

        if dataByFilename.has_key(base_filename_nl):
            print "collision for %s at %d and %d" %(base_filename_nl, i,dataByFilename[base_filename_nl]['num'] )
        dataByFilename[base_filename_nl]=dict(title_nl=title_nl, title_fr=title_fr, 
            descr_nl=descr_nl, descr_fr=descr_fr, date=date, num=i)

        i+=1
    
    return dataByFilename


def doit(self, path_to_file=""):
    print "\n\n\nsetPublicationData from BeSWIC list"
    if not path_to_file:
        return "please supply path_to_file that contains the necessary data"
    if not os.access(path_to_file, os.F_OK):
        return "Could not open file at %s" % path_to_file
    fh = open(path_to_file, 'r')
    data = fh.read()
    fh.close()
    
    dataByFilename = parseData(data)
    print len(dataByFilename.keys())
    files = self.objectItems('ATBlob')
    for fname, fobj in files:
        lang, base_filename, file_ext =  split_filename(fname, LANGUAGES)
        if lang!=fobj.Language():
            print "ERROR! lang and actual language don't match on %s" %(fname)
            continue
        print  lang, base_filename, file_ext
        data = dataByFilename.get(base_filename, None)
        if not data:
            print "ERROR! No data found for %s" %(fname)
            import pdb; pdb.set_trace()
            continue
        title = data.get('title_%s' %lang)
        descr = data.get('descr_%s' %lang)
        date = data.get('date')
        fobj.setTitle(title)
        fobj.setDescription(descr)
        fobj.setEffectiveDate(date)
        fobj.reindexObject()
    
    
    print "wtf?"
    return "done - no problems"
    