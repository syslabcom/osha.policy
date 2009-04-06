from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner

from Products.CMFCore.utils import getToolByName


def run(self):
    """ """
    for o in queryObjs(self):
        import pdb; pdb.set_trace()
        fs = getRichTextFields(o)
        for f in fs:
            text = santize(self, f.get(), documentCleaner)

def queryObjs(self):
    portal_type = self.REQUEST.get('portal_type', 'OSH⊇Link')
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


