#from lxml.etree import parse, Element, tostring
from elementtree.ElementTree import parse, Element, tostring
from xlrd import open_workbook
import logging
import sys

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
        tassert termIdentifier not in self.tree.items.keys()
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
            parentTerm.insert(last_brother, new_term)
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
        # how to get descriptions?
        import pdb;pdb.set_trace()
        term.remove(term[1])
        term.insert(1, caption)

    def untranslated_ids(self):
        return self.id, self.caption, self.description

class MoveCommand(BaseCommand):
    def __init__(self, tree,  old, new, new_father):
        self.tree = tree
        self.old = old
        self.new = new
        self.new_father = new_father

    def run(self):
        old_child = self.tree.items[self.old]
        old_father = self.tree.fathers[old_child]
        new = self.new
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
            parentTerm.insert(last_brother, old_child)
        if not has_brothers:
            parentTerm.insert(index, old_child)
        old_father.remove(old_child)

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
        treeCaption = Element('caption')
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
    tokens = line.split('|')
    cmd_token = tokens[0]
    args = tokens[1:]
    cmd = {'c' : CreateCommand,
           'u' : UpdateCommand,
           'm' : MoveCommand,
           'd' : DeleteCommand}[cmd_token](tree, *args)
    return cmd

def get_xls(filename):
    book = open_workbook(file_contents=file(filename).read())
    sheet = book.sheets()[0]
    return sheet

if __name__ == '__main__':
    if len(sys.argv) > 2:
        thesaurus_file = sys.argv[2]
    else:
        thesaurus_file = './src/osha/policy/data/vocabularies/MultilingualThesaurus.vdex'
    tree = Tree(thesaurus_file)
    translations = []
    for line in file(sys.argv[1]):
        print line
        instance = cmd_parser(line, tree)
        instance.run()
        translations.append(instance.untranslated_ids())
        tree.update()
    tree.close()
