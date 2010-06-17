#from lxml.etree import parse, Element, tostring
from elementtree.ElementTree import parse, Element, tostring
from xlrd import open_workbook
import csv
import logging
import sys

def get_xls(filename):
    book = open_workbook(file_contents=file(filename).read())
    sheet = book.sheets()[0]
    return sheet

class Command(object):
    def __init__(self, command_type, original_id = None, old_id = None,
                 new_move_id = None, create_id = None, caption = None,
                 description = None, parent_id = None):
        self.command_type = command_type
        self.original_id = original_id
        self.old_id = old_id
        self.new_move_id = new_move_id
        self.create_id = create_id
        self.caption = caption
        self.description = description
        self.parent_id = parent_id

    def __cmp__(self, other):
        our_level = (self.old_id and self.old_id[-1]) or (self.original_id and self.original_id[-1]) or (self.new_move_id and self.new_move_id[-1]) or (self.create_id and self.create_id[-1])
        their_level = (other.old_id and other.old_id[-1]) or (self.original_id and self.original_id[-1]) or (other.new_move_id and other.new_move_id[-1]) or (other.create_id and other.create_id[-1])
        if our_level != their_level:
            if our_level < their_level:
                return 1
            return -1
        else:
            for order in ('c', 'm', 'd', 'u'):
                if self.command_type == order:
                    return -1
                if other.command_type == order:
                    return 1

    def show_cmd(self):
        cmd, original_id, old_id, new_move_id, create_id, caption, description, parent_id = \
            self.command_type, self.original_id, self.old_id, self.new_move_id, self.create_id, self.caption, \
            self.description, self.parent_id
        if cmd == 'c':
            return '|'.join((cmd, create_id, parent_id, caption, description))
        if cmd == 'u':
            return '|'.join((cmd, original_id, caption, description))
        if cmd == 'm':
            return '|'.join((cmd, old_id, new_move_id, parent_id))
        if cmd == 'd':
            return '|'.join((cmd, old_id))

def converter():
    try:
        _converter()
    except Exception, e:
        print e
        import pdb;pdb.post_mortem(sys.exc_traceback)

def _converter():
    sheet = get_xls(sys.argv[1])

    commands = []
    for i in range(sheet.nrows):
        row = sheet.row(i)
        command = row[9].value.lower().strip()
        create_id = row[10].value
        old_id = row[13].value.strip()
        original_id = row[0].value.strip()
        new_move_id = row[14].value.strip()
        caption = row[11].value.strip()
        description = row[12].value.strip()
        parent_id = row[17].value.strip()
        args = (original_id, old_id, new_move_id, create_id, caption, description, parent_id)

        if not (command or old_id):
            continue
        if command == 'new term':
            if old_id:
                #Howdy, this is not a new term, this is a move and rename action
                commands.append(Command('u', original_id = new_move_id, caption = caption, description = description))
                commands.append(Command('m', original_id = original_id, old_id = old_id, new_move_id = new_move_id, caption = caption, parent_id = parent_id))
            else:
                commands.append(Command('c', create_id = create_id, parent_id = parent_id, caption = caption, description = description))
        elif command == 'amend term':
            commands.append(Command('u', original_id = original_id, caption = caption, description = description))
            if old_id:
                #Howdy, that is ALSO a hidden move. How sneaky!
                commands.append(Command('m', original_id = original_id, old_id = old_id, new_move_id = new_move_id, caption = caption, parent_id = parent_id))
        elif command == 'delete term' and not old_id:
            commands.append(Command('d', old_id = old_id))
        elif old_id and not command == u'accept / reject':
            commands.append(Command('m', old_id = old_id, new_move_id = new_move_id, caption = caption, parent_id = parent_id))
        elif command == u'accept / reject':
            continue
        else:
            raise Exception("Unknown case")

    cleaning = True
    while cleaning:
        cleaning = False
        id_to_command = {}
        for command in commands:
            if command.command_type == 'm':
                if not id_to_command.has_key(command.old_id):
                    id_to_command[command.old_id] = []
                id_to_command[command.old_id].append(command)
        for cmds in id_to_command.values():
            removes = set()
            for key in cmds[0].__dict__.keys():
                different_values = len(set([getattr(x, key) for x in cmds if getattr(x, key)]))
                if key == 'parent_id' and different_values > 1:
                    parents = [int(x.parent_id[:-1]) for x in cmds if x.parent_id]
                    new_id = int(cmds[0].new_move_id[:-1])
                    closest_parent = ''
                    closest = 99999999999999
                    for cmd in cmds:
                        parent_distance = cmd.parent_id and new_id - int(cmd.parent_id[:-1]) or 999999999999999
                        if parent_distance > 0 and closest > parent_distance:
                            closest_parent = cmd
                            closest = parent_distance
                    removes.update([x for x in cmds if x.parent_id != closest_parent.parent_id])
                    continue
                assert different_values <= 1, "Two move lines have different data. Key: '%s', values: '%s'" % (key, '|'.join([getattr(x, key) for x in cmds]))
                if different_values:
                    removes.update([x for x in cmds if not getattr(x, key)])
            if not cmds[0].old_id in ['61721D', '18201F']:
                assert (set(cmds) - removes).pop()
            for cmd in removes:
                commands.remove(cmd)
                cleaning = True
                break
    commands.sort()
    for command in commands:
        print command.show_cmd()


NS = '{http://www.imsglobal.org/xsd/imsvdex_v1p0}'

debugging_handler = logging.StreamHandler()
debugging_log = logging.getLogger('debugging_log')
debugging_log.addHandler(debugging_handler)
debugging_log.setLevel(logging.WARN)

class BaseCommand(object):
    def run(self):
        return NotImplemented()

    def untranslated_ids(self):
        return NotImplemented

class CreateCommand(BaseCommand):
    def __init__(self, tree, id, parent_id, caption, description):
        self.tree = tree
        self.id = id
        self.parent_id = parent_id
        self.caption = caption
        self.description = description

    def run(self):
        termIdentifier = self.id
        termCaption = self.caption
        termDescription = self.description
        assert termIdentifier not in self.tree.items.keys()
        parentTerm = self.tree.items[self.parent_id]
        new_term =  self.tree.new_tree_term(termIdentifier, termCaption, termDescription)
        last_brother = None
        has_brothers = False
        insert_check = False
        for index, brother in enumerate(parentTerm):
            if brother.tag != NS + 'term':
                continue
            else:
                has_brothers = True
            brotherTermIdentifier = brother[0].text
            if termIdentifier < brotherTermIdentifier:
                insert_check = True
                parentTerm.insert(index, new_term)
                last_brother = None
                break
            last_brother = index
        if last_brother:
            insert_check = True
            parentTerm.insert(last_brother + 1, new_term)
        if not has_brothers:
            insert_check = True
            parentTerm.insert(index, new_term)
        assert insert_check

    def untranslated_ids(self):
        return self.id, self.caption, self.description

class UpdateCommand(BaseCommand):
    def __init__(self, tree, id, caption, description):
        self.tree = tree
        self.id = id
        self.caption = caption
        self.description = description

    def run(self):
        term = self.tree.items[self.id]
        new_term = self.tree.new_tree_term('ignore', self.caption, self.description)
        caption = new_term[1]
        description = new_term[2]
        term.remove(term[1])
        term.insert(1, caption)
        for i in range(20):
            if term[i].tag == '{http://www.imsglobal.org/xsd/imsvdex_v1p0}description':
                break
        term.remove(term[i])
        term.insert(i, description)

    def untranslated_ids(self):
        return self.id, self.caption, self.description

class MoveCommand(BaseCommand):
    def __init__(self, tree,  old, new, new_father, keep_names):
        self.keep_names = 'keep_names' == keep_names.lower()
        self.tree = tree
        self.old = old
        self.new = new
        self.new_father = new_father

    def run(self):
        old_child = self.tree.items[self.old]
        old_father = self.tree.fathers[old_child]
        old_father.remove(old_child)
        new = self.new
        if new in self.tree.items.keys():
            if not self.keep_names:
                caption = old_child[1]
                description = old_child[2]
                new.remove(new[1])
                new.insert(1, caption)
                for i in range(20):
                    if new[i].tag == '{http://www.imsglobal.org/xsd/imsvdex_v1p0}description':
                        break
                new.remove(new[i])
                new.insert(i, description)

            return
        parentTerm = self.tree.items[self.new_father]
        last_brother = None
        has_brothers = False
        for index, brother in enumerate(parentTerm):
            if brother.tag != NS + 'term':
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
            parentTerm.insert(last_brother + 1, old_child)
        if not has_brothers:
            parentTerm.insert(index, old_child)

        old_child[0].text = new

    def untranslated_ids(self):
        return None

class DeleteCommand(BaseCommand):
    def __init__(self, tree, id):
        self.tree = tree
        self.id = id

    def run(self):
        kid_id = self.id
        kid = self.tree.items[kid_id]
        father = self.tree.fathers[kid]
        father.remove(kid)
        return False

    def untranslated_ids(self):
        return None

class Tree(object):
    def __init__(self, thesaurus_file):
        self.__tree = parse(thesaurus_file)
        self.all_languages = set([x.get('language') for x in self.__tree.findall('.//%slangstring' % NS)])
        self.update()

    def update(self):
        self.fathers = {}
        self.items = {}
        for term in self.__tree.findall('.//%sterm' % NS):
            self.items[term[0].text] = term
        for term in self.__tree.findall('//%sterm' % NS):
            for child in term:
                self.fathers[child] = term

    def new_tree_term(self, termIdentifier, caption, description):
        term = Element(NS + 'term')
        treeTermIdentifier = Element(NS + 'termIdentifier')
        treeTermIdentifier.text = termIdentifier
        term.append(treeTermIdentifier)
        treeCaption = Element(NS + 'caption')
        self.addLangs(treeCaption, caption)
        term.append(treeCaption)
        treeDesc = Element('description')
        self.addLangs(treeDesc, description)
        term.append(treeDesc)
        return term

    def addLangs(self, element, msg):
        for lang in self.all_languages:
            elem = Element(NS + 'langstring')
            elem.set('language', lang)
            elem.text = msg
            element.append(elem)

    def close(self):
        self.__tree.write('out.xml', 'utf-8')

def cmd_parser(line, tree):
    tokens = line.strip().split('|')
    cmd_token = tokens[0]
    args = tokens[1:]
    cmd = {'c' : CreateCommand,
           'u' : UpdateCommand,
           'm' : MoveCommand,
           'd' : DeleteCommand}[cmd_token](tree, *args)
    return cmd

def vdexupdater():
    try:
        _vdexupdater()
    except Exception, e:
        print e
        import pdb;pdb.post_mortem(sys.exc_traceback)


def _vdexupdater():
    if len(sys.argv) > 2:
        thesaurus_file = sys.argv[2]
    else:
        thesaurus_file = './src/osha/policy/data/vocabularies/MultilingualThesaurus.vdex'
    tree = Tree(thesaurus_file)
    translations = []
    for line in file(sys.argv[1]):
        print line
        #print '23064E' in tostring(tree._Tree__tree.getroot())
        instance = cmd_parser(line, tree)
        instance.run()
        translations.append(instance.untranslated_ids())
        tree.update()
    tree.close()

def xmltoxls():
    try:
        _xmltoxls()
    except Exception, e:
        print e
        import pdb;pdb.post_mortem(sys.exc_traceback)

def _xmltoxls():
    if len(sys.argv) > 1:
        xml = parse(sys.argv[1])
    else:
        xml = parse('out.xml')
    out = csv.DictWriter(file('out.csv', 'w'), ['id', 'levela', 'levelb', 'levelc', 'leveld', 'levele', 'levelf', 'levelg', 'levelh', 'translations'])
    for term in xml.findall('.//%sterm' % NS):
        id = term.find('%stermIdentifier' % NS).text
        level = 'level' + id[-1].lower()
        caption = [x.text for x in term.findall('%scaption/%slangstring' % (NS, NS)) if x.attrib['language'] == 'en'][0].encode('ascii', 'ignore')
        translations = len(set([x.text for x in term.findall('%scaption/%slangstring' % (NS, NS))]))
        new_row = {}
        new_row['id'] = id
        new_row[level] = caption
        new_row['translations'] = translations
        print id, new_row.keys()
        out.writerow(new_row)

def ordervdex():
    try:
        _ordervdex()
    except Exception, e:
        print e
        import pdb;pdb.post_mortem(sys.exc_traceback)

def _ordervdex():
    if len(sys.argv) > 1:
        vdex_filename = sys.argv[1]
    else:
        vdex_filename = 'out.xml'
    vdex = parse(vdex_filename)
    orderNode(vdex.getroot())
    vdex.write(vdex_filename, 'utf-8')

def orderNode(node):
    terms = [(index, x) for (index, x) in enumerate(node) if x.tag.endswith('term')]
    current_order = [x[0] for x in terms]
    map(orderNode, [x[1] for x in terms])
    sorter = lambda a, b: unicode(a[1][0].text.strip()).__cmp__(unicode(b[1][0].text.strip()))
    terms.sort(sorter)
    new_order = [x[0] for x in terms]
    if new_order != current_order:
        print "%s has unsorted children" % node[0].text
        for ((ignore, term), new_pos) in zip(terms, current_order):
            node.remove(term)
            node.insert(new_pos, term)


