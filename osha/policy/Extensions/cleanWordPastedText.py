from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner

from Produts.Archetype.Widget import RichWidget
from Products.CMFCore.utils import getToolByName


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
                text = santize(self, f.get(), documentCleaner)
                f.set(text)
    return 'Cleaned up %d fields in %d %s objects' % (num_fs, num_o, portal_type)

def queryObjs(self, portal_type):
    catalog = getToolByName(self, 'portal_catalog')
    return [o.getObject() for o in catalog(portal_type=portal_type)]

def getRichTextFields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]

def documentCleaner(self):
    return Cleaner(
                page_structure = False,
                remove_unknown_tags = True,
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


