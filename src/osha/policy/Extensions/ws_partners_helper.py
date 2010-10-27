import re
from OFS.Image import File
from logging import getLogger
log = getLogger('osha.policy::ws_partners_helper')

REPLACE = {
    "True": True,
    "False": False,
    "None": None
    }

def parsePartners(self, txt, size):
    partners = dict()
    if type(txt) == type(''):
        txt = unicode(txt, 'utf-8')
    lines = txt.split('\n')
    for line in lines:
        # eval is evil, I know.... but here it's so handy!
        try:
            li = eval(line)
            if len(li) != size:
                log.error('Got a line of size %d, but it should be %d' % (len(li),
                    size))
            else:
                vals = [REPLACE.get(x, x) for x in li]
                partners[li[0]] = vals
        except:
            log.error("Could not eval line: %s" % line)
    return partners

def setAttachment(ob, file, filename):
  if len(file.data) == 0:
    return
  mutator = ob.getField('attachment').getMutator(ob)
  fileob = File(filename, filename, file.data)
  setattr(fileob, 'filename', filename)
  mutator(fileob)


def setImage(ob, image):

    ob.setImage(image.data)
    return 1

