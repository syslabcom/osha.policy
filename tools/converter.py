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
    def __init__(self, command_type, old_id, new_id, caption, description, parent_id):
        self.command_type = command_type
        self.old_id = old_id
        self.new_id = new_id
        self.caption = caption
        self.description = description
        self.parent_id = parent_id

commands = []
for i in range(sheet.nrows):
    row = sheet.row(i)
    command = row[9].value.lower()
    old_id = row[13].value
    new_id = row[14].value.strip()
    caption = row[11].value.strip()
    description = row[12].value.strip()
    parent_id = row[17].value.strip()
    args = (old_id, new_id, caption, description, parent_id)

    if not (command or old_id):
        continue
    if command == 'new term':
        if old_id:
            #Howdy, this is not a new term, this is a move and rename action
            commands.append(Command('u', *args))
            commands.append(Command('m', *args))
        else:
            commands.append(Command('r', *args))
    elif command == 'amend term':
        commands.append(Command('u', *args))
        if old_id:
            #Howdy, that is ALSO a hidden move. How sneaky!
            commands.append(Command('m', *args))
    elif command == 'delete term' and not old_id:
        commands.append(Command('d', *args))
    elif old_id and not command == u'accept / reject':
        commands.append(Command('m', *args))
    elif command == u'accept / reject':
        continue
    else:
        raise Exception("Unknown case")
