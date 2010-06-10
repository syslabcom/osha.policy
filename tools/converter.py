#from lxml.etree import parse, Element, tostring
from elementtree.ElementTree import parse, Element, tostring
from xlrd import open_workbook
import logging
import logging.handlers
import sys

def get_xls(filename):
    book = open_workbook(file_contents=file(filename).read())
    sheet = book.sheets()[0]
    return sheet

sheet = get_xls('./new_thesaurus3.xls')
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
                return -1
            return 1
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
            return '|'.join((cmd, old_id, new_move_id, caption, parent_id))
        if cmd == 'd':
            return '|'.join((cmd, old_id))

commands = []
for i in range(sheet.nrows):
    row = sheet.row(i)
    command = row[9].value.lower()
    create_id = row[10].value
    old_id = row[13].value
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
            commands.append(Command('m', old_id = old_id, new_move_id = new_move_id, caption = caption, parent_id = parent_id))
        else:
            commands.append(Command('c', create_id = create_id, parent_id = parent_id, caption = caption, description = description))
    elif command == 'amend term':
        commands.append(Command('u', original_id = original_id, caption = caption, description = description))
        if old_id:
            #Howdy, that is ALSO a hidden move. How sneaky!
            commands.append(Command('m', old_id = old_id, new_move_id = new_move_id, caption = caption, parent_id = parent_id))
    elif command == 'delete term' and not old_id:
        commands.append(Command('d', old_id = old_id))
    elif old_id and not command == u'accept / reject':
        commands.append(Command('m', old_id = old_id, new_move_id = new_move_id, caption = caption, parent_id = parent_id))
    elif command == u'accept / reject':
        continue
    else:
        raise Exception("Unknown case")

commands.sort()
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
            assert different_values <= 1
            if different_values:
                removes.update([x for x in cmds if not getattr(x, key)])
        assert (set(cmds) - removes).pop()
        for cmd in removes:
            commands.remove(cmd)
            cleaning = True
            break
        import pdb;pdb.set_trace()
        
for command in commands:
    print command.show_cmd()

