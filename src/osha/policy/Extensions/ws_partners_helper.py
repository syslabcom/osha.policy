import re
from logging import getLogger
log = getLogger('osha.policy::ws_partners_helper')

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
                partners[li[0]] = li
        except:
            log.error("Could not eval line: %s" % line)
    return partners
