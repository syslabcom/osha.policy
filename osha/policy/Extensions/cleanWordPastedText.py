import logging
import transaction

from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner

from Products.Archetypes.Widget import RichWidget
from Products.CMFCore.utils import getToolByName

log = logging.getLogger('cleanWordPastedText')

def run(self):
    """ """
    num_fs = 0
    num_o = 0
    portal_type = self.REQUEST.get('portal_type', 'OSH_Link')
    for o in queryObjs(self, portal_type):
        fs = getRichTextFields(o)
        num_fs += len(fs)
        if len(fs):
            num_o += 1
            for f in fs:
                text = sanitize(self, f.getAccessor(o)(), documentCleaner())
                f.getMutator(o)(text)
        if not num_o%1000:
            transaction.commit()
            log.info('transaction.commit(), %d' % num_o)
    t = 'Cleaned up %d fields in %d %s objects' % (num_fs, num_o, portal_type)
    log.info(t)
    return t 

def queryObjs(self, portal_type):
    catalog = getToolByName(self, 'portal_catalog')
    return [o.getObject() for o in catalog(portal_type=portal_type)]

def getRichTextFields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]

def documentCleaner():
    return Cleaner(
                page_structure = False,
                remove_unknown_tags = False,
                safe_attrs_only = True,
                allow_tags = [ "blockquote", "a", "em", "p", "strong" ],
                scripts = False,
                javascript = False,
                comments = False,
                style = False,
                links = False, 
                meta = False,
                processing_instructions = False,
                frames = False,
                annoying_tags = False)

def sanitize(self, input, cleaner):
    fragments=html.fragments_fromstring(input)
    output=[]

    for fragment in fragments:
        if isinstance(fragment, basestring):
            output.append(fragment)
        else:
            try:
                cleaned=cleaner.clean_html(fragment)
                output.append(etree.tostring(cleaned, encoding=unicode))
            except AssertionError:
                # This happens if the cleaner tries to strip the top-level
                # element
                output.extend(filter(None, [fragment.text, fragment.tail]))
                continue

    return u"".join(output)


