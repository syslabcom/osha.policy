from pyPdf.pdf import ContentStream
from pyPdf.generic import *

def logit(*kwargs):
    " log something from the web "
    try:
        mesg = ''
        for kwarg in kwargs:
            mesg += str(kwarg) + ' '
        print mesg
    except:
        print [kwargs]

def extractPDFText(self):
    text = u""
    content = self["/Contents"].getObject()
    if not isinstance(content, ContentStream):
        content = ContentStream(content, self.pdf)
    # Note: we check all strings are TextStringObjects.  ByteStringObjects
    # are strings where the byte->string encoding was unknown, so adding
    # them to the text here would be gibberish.
    for operands,operator in content.operations:
        if operator == "Tj":
            _text = operands[0]
            if isinstance(_text, TextStringObject):
                text += _text
        elif operator == "T*":
            text += "\n"
        elif operator == "'":
            text += "\n"
            _text = operands[0]
            if isinstance(_text, TextStringObject):
                text += operands[0]
        elif operator == '"':
            _text = operands[2]
            if isinstance(_text, TextStringObject):
                text += "\n"
                text += _text
        elif operator == "TJ":
            for i in operands[0]:
                if isinstance(i, TextStringObject):
                    text += i
        elif operator == "k":
            text += "\n" 
    return text

