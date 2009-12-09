from elementtree.ElementTree import parse, Element, tostring
from xlrd import open_workbook

tree = parse('./src/osha/policy/data/vocabularies/MultilingualThesaurus.vdex')

ns = '{http://www.imsglobal.org/xsd/imsvdex_v1p0}'

items = {}

def get_xls(filename):
    book = open_workbook(file_contents=file(filename).read())
    sheet = book.sheets()[0]
    return sheet
for term in tree.findall('.//%sterm' % ns):
    items[term[0].text] = term
fathers = {}
for term in tree.findall('//%sterm' % ns):
    for child in term:
        fathers[child] = term.text

# All languages
all_languages = set([x.get('language') for x in tree.findall('.//%slangstring' % ns)])
#This mapping quickly adds captions for all languages
def addLangs(element, msg):
    for lang in all_languages:
        elem = Element(ns + 'langstring')
        elem.set('language', lang)
        elem.text = msg
        element.append(elem)

def new_tree_term(termIdentifier, caption, description):
    term = Element(ns + 'term')
    treeTermIdentifier = Element(ns + 'termIdentifier')
    treeTermIdentifier.text = termIdentifier
    term.append(treeTermIdentifier)
    treeCaption = Element('caption')
    addLangs(treeCaption, caption)
    term.append(treeCaption)
    treeDesc = Element('description')
    addLangs(treeDesc, description)
    term.append(treeDesc)
    return term
    
    
new_terms = []
def register_new_term(line, row):
    new_terms.append((line, row))

def new_term(wrapped):
    line, row = wrapped
    termIdentifier = row[10].value
    termCaption = row[11].value
    termDescription = row[12].value
    assert termIdentifier not in items.keys()
    try:
        parentTerm = items[row[17].value.strip()]
    except KeyError:
        print 'Line %i Can not add new term, provided information is wrong, Father does not exist' % (line)
        return True
    new_term =  new_tree_term(termIdentifier, termCaption, termDescription)
    last_brother = None
    for index, brother in enumerate(parentTerm):
        if brother.tag != ns + 'term':
            continue
        brotherTermIdentifier = brother[0].text
        if termIdentifier < brotherTermIdentifier:
            parentTerm.insert(index, new_term)
            break
    return False

amended_terms = []
def register_amend_term(line, row):
    amended_terms.append((line, row))

def amend_term(wrapped):
    line, row = wrapped
    try:
        term = items[row[0].value]
    except KeyError:
        print "Line: %i Can not amend term, if term id is missing" % (line)
        return True
    new_term = new_tree_term('ignore', row[11].value, 'ignore')
    caption = new_term[1]
    term.remove(term[1])
    term.insert(1, caption)
    return False

moved_terms = {}
def register_move_term(line, row):
    old = row[13].value
    new = row[14].value
    father = row[17].value
    if not moved_terms.has_key(old):
        moved_terms[old] = {}
    data = moved_terms[old]
    if not data.has_key('lines'):
        data['lines'] = []
    data['lines'].append(line)
    if not data.has_key('new'):
        data['new'] = new
    assert data['new'] == new, "For the key %s two entries exist that do not agree, where to add the new key to: 1: %s, 2:%s" % (old, data['new'], new)
    if not data.get('father', '') and father:
        data['father'] = father
    if father:
        assert data.get('father', '') == father, str((data['father'], '=', father))
def move_term(old, data):
    try:
        old_child = items[old]
    except:
        print "Lines: %s Cannot move term, because old id does not exist" % (data['lines'])
        return True
    try:
        old_father = items[fathers[old_child]]
    except:
        print "Lines: %s This cannot be moved, father of %s unknown" % (str(data['lines']), items[old][0].text)
        return True
    old_father.remove(old_child)
    new = data['new']
    father = items[data['father']]
    old_child[0].text = new
    for index, brother in enumerate(parentTerm):
        if brother.tag != ns + 'term':
            continue
        brotherTermIdentifier = brother[0].text
        if new < brotherTermIdentifier:
            parentTerm.insert(index, old_child)
            break
    return False
   

deleted_terms = []
def register_delete_term(line, row):
    deleted_terms.append((line, row))

def delete_term(wrapped):
    i, row = wrapped
    try:
        father = items[row[17].value]
        kid = items[row[0].value]
        father.remove(kid)
    except KeyError:
        print 'Line %i Can not delete, because information is incomplete' % (i)
        return True
    return False
        

sheet = get_xls('./new_thesaurus.xls')
for i in range(sheet.nrows):
    row = sheet.row(i)
    if not (row[9].value or row[13].value):
        continue
    if row[9].value.lower() == 'new term' and not row[13].value:
        register_new_term(i+1, row)
    elif row[9].value.lower() == 'amend term' and not row[13].value:
        register_amend_term(i+1, row)
    elif row[9].value.lower() == 'delete term' and not row[13].value:
        register_delete_term(i+1, row)
    elif row[13].value and not row[9].value == u'Accept / Reject':
        try:
            register_move_term(i+1, row)
        except AssertionError, e:
            print e
    elif row[9].value == u'Accept / Reject':
        continue
    else:
        print row
        break

filter(delete_term, deleted_terms)
filter(new_term, new_terms)
filter(amend_term, amended_terms)
for key, value in moved_terms.items():
    move_term(key, value)

tree.write('out.xml')
    
