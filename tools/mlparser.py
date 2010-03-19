#from lxml.etree import parse, Element, tostring
from elementtree.ElementTree import parse, Element, tostring
from xlrd import open_workbook
import logging
import logging.handlers

tree = parse('./src/osha/policy/data/vocabularies/MultilingualThesaurus.vdex')

ns = '{http://www.imsglobal.org/xsd/imsvdex_v1p0}'

osha_handler = logging.FileHandler('osha.log')
reindex_handler = logging.FileHandler('reindex.log')
debugging_handler = logging.StreamHandler()

osha_log = logging.getLogger('osha_log')
reindex_log = logging.getLogger('reindex_log')
debugging_log = logging.getLogger('debugging_log')

osha_log.addHandler(osha_handler)
reindex_log.addHandler(reindex_handler)
debugging_log.addHandler(debugging_handler)

debugging_log.setLevel(logging.WARN)
osha_log.setLevel(logging.DEBUG)
reindex_log.setLevel(logging.DEBUG)

deleted_fathers = []

renamed_keys = {}


items = {}

def get_xls(filename):
    book = open_workbook(file_contents=file(filename).read())
    sheet = book.sheets()[0]
    return sheet

fathers = {}
def updateCaches():
    for key in fathers.keys():
        fathers.pop(key)
    for key in items.keys():
        items.pop(key)
    while deleted_fathers:
        deleted_fathers.pop()
    for term in tree.findall('.//%sterm' % ns):
        debugging_log.debug('terms: \"%s\"', term[0].text)
        items[term[0].text] = term
    for term in tree.findall('//%sterm' % ns):
        for child in term:
            fathers[child] = term.getchildren()[0].text

updateCaches()
original_fathers = {}
for key, value in  fathers.items():
    original_fathers[key] = value

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

def new_term(wrapped, errors):
    line, row = wrapped
    termIdentifier = row[10].value
    termCaption = row[11].value
    termDescription = row[12].value
    assert termIdentifier not in items.keys()
    try:
        debugging_log.debug(row[17].value.strip())
        parentTerm = items[row[17].value.strip()]
        debugging_log.debug('parent term found')
    except KeyError:
        errors.append('Line %i Can not add new term, provided information is wrong, Father "%s" does not exist' % (line, row[17].value.strip()))
        return True
    new_term =  new_tree_term(termIdentifier, termCaption, termDescription)
    last_brother = None
    has_brothers = False
    for index, brother in enumerate(parentTerm):
        if brother.tag != ns + 'term':
            continue
        else:
            has_brothers = True
        brotherTermIdentifier = brother[0].text
        if termIdentifier < brotherTermIdentifier:
            parentTerm.insert(index, new_term)
            last_brother = None
            break
        last_brother = index
    if last_brother:
        parentTerm.insert(last_brother, new_term)
    if not has_brothers:
        parentTerm.insert(index, new_term)
    return False

amended_terms = []
def register_amend_term(line, row):
    amended_terms.append((line, row))

def amend_term(wrapped, errors):
    line, row = wrapped
    try:
        term = items[row[0].value]
    except KeyError:
        errors.append("Line: %i Can not amend term, if term id is missing" % line)
        return True
    new_term = new_tree_term('ignore', row[11].value, 'ignore')
    caption = new_term[1]
    term.remove(term[1])
    term.insert(1, caption)
    return False

moved_terms = {}
def register_move_term(line, row):
    old = row[13].value.strip()
    new = row[14].value.strip()
    if '+' in old:
        count = 0
        for one_old in old.split('+'):
            count += 1
            fake = count > 1
            one_old = one_old.strip()
            if inner_register_move_term(line, row, one_old, new, fake):
                return True
        return False
    else:
        return inner_register_move_term(line, row, old, new, False)

def inner_register_move_term(line, row, old, new, fake_move):
    father = row[17].value.strip()
    if not moved_terms.has_key(old):
        moved_terms[old] = {}
    data = moved_terms[old]
    data['fake'] = data.get('fake', False) or fake_move
    if not data.has_key('lines'):
        data['lines'] = []
    data['lines'].append(line)
    if not data.has_key('new'):
        data['new'] = new
    if data['new'] != new:
        data['error'] = "Lines: %s For the key %s two entries exist that do not agree, where to add the new key to: 1: %s, 2:%s" % (data['lines'], old, data['new'], new)
    type = row[9].value.strip()
    if father:
        if not data.get('father', ''):
            data['father'] = father
            if type == 'New term':
                data['father_authorative'] = True
            else:
                data['father_authorative'] = False
        else:
            if data.get('father', '') != father:
                problem = 'Lines: %s identifiers %s of broader term do not match for the involved lines' % (str(data['lines']), ', '.join(['"%s"' % x for x in [data['father'], father]]))
                if type == 'New term':
                    if not data['father_authorative']:
                        data['father_authorative'] = True
                        data['father'] = father
                        #debugging_log.warning(problem)
                    else:
                        data['error'] = problem
                else:
                    pass
                    #debugging_log.warning(problem)
def move_term(old, data, errors):
    if len(data['lines']) == 1:
        errors.append('Lines: %s I was asked to perform a move operation, but I have only one excel line related to it.' % str(data['lines']))
        return True
    if data.has_key('error'):
        errors.append('Lines: %s Cannot move term, %s' % (data['lines'], data['error']))
        return True
    try:
        old_child = items[old]
    except KeyError:
        errors.append("Lines: %s Cannot move term, because old id does not exist" % data['lines'])
        return True
    try:
        old_father_id = original_fathers[old_child]
        try:
            old_father = items[old_father_id]
        except KeyError:
            old_father = items[renamed_keys[old_father_id]]
    except KeyError:
        errors.append("Lines: %s This cannot be moved, father of %s unknown" %(str(data['lines']), items[old][0].text))
        return True
    new = data['new']
    try:
        data['father']
    except KeyError:
        errors.append('Lines: %s missing new parent, where shall I add the category?' % str(data['lines']))
        return True
    try:
        parentTerm = items[data['father']]
    except KeyError:
        try:
            parentTerm = items[renamed_keys[data['father']]]
        except KeyError:
            errors.append("Lines: %s parent \"%s\" not found, don't know where to add" % (str(data['lines']), data['father']))
            return True
    if data['fake'] or new in items.keys():
        reindex_log.info('move old-new: %s-%s' % (old, new))
        return False
    renamed_keys[old_child[0].text] = new
    old_child[0].text = new
    last_brother = None
    has_brothers = False
    for index, brother in enumerate(parentTerm):
        if brother.tag != ns + 'term':
            continue
        else:
            has_brothers = True
        brotherTermIdentifier = brother[0].text
        if new < brotherTermIdentifier:
            parentTerm.insert(index, old_child)
            last_brother = None
            break
        last_brother = index
    if last_brother:
        parentTerm.insert(last_brother, old_child)
    if not has_brothers:
        parentTerm.insert(index, old_child)
    deleted_fathers.append(old)
    old_father.remove(old_child)
    reindex_log.info('move old-new: %s-%s' % (old, new))
    return False

deleted_terms = []
def register_delete_term(line, row):
    deleted_terms.append((line, row))

def delete_term(wrapped, errors):
    i, row = wrapped
    kid_id = row[0].value
    kid = items[kid_id]
    father_id = fathers[kid]
    father = items[father_id]
    father.remove(kid)
    reindex_log.info('Delete key: %s' % kid_id)
    return False

sheet = get_xls('./new_thesaurus3.xls')
for i in range(sheet.nrows):
    row = sheet.row(i)
    if not (row[9].value or row[13].value):
        continue
    if row[9].value.lower() == 'new term' and not row[13].value:
        register_new_term(i+1, row)
    elif row[9].value.lower() == 'amend term':# and not row[13].value:
        register_amend_term(i+1, row)
        if row[13].value:
            register_move_term(i+1, row)
    elif row[9].value.lower() == 'delete term' and not row[13].value:
        register_delete_term(i+1, row)
    elif row[13].value and not row[9].value == u'Accept / Reject':
        try:
            register_move_term(i+1, row)
        except AssertionError, e:
            debugging_log.exception("Something went wrong")
    elif row[9].value == u'Accept / Reject':
        continue
    else:
        debugging_log.error("Unknown task: %s", row)
        break

old_tasks = -1
tasks = 0
while old_tasks != tasks:
    errors = []
    old_tasks = tasks
    debugging_log.info('Tasks: %i', tasks)
    new_new_terms = []
    for term in new_terms:
        if new_term(term, errors):
            new_new_terms.append(term)
    new_terms = new_new_terms
    new_amended_terms = []
    for term in amended_terms:
        if amend_term(term, errors):
            new_amended_terms.append(term)
    amended_terms = new_amended_terms
    new_moved_terms = {}
    moved_terms_as_items = moved_terms.items()
    def custom_sort(b, a):
        if a[0] in tostring(items[b[0]]):
            return 1
        return -1
    moved_terms_as_items.sort(custom_sort)
    for key, value in moved_terms_as_items:
        if move_term(key, value, errors):
            new_moved_terms[key] = value
    moved_terms = new_moved_terms
    tasks = len(deleted_terms) + len(new_terms) + len(amended_terms) + len(moved_terms)
    updateCaches()

new_deleted_terms = []
for term in deleted_terms:
    if delete_term(term, errors):
        new_deleted_terms.append(term)
deleted_terms = new_deleted_terms

errors = list(set(errors))
errors.sort()
for error in errors:
    osha_log.warning(error)

tree.write('out.xml', 'utf-8')
    
