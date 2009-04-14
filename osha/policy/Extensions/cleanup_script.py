import logging
import transaction
from types import *
from lxml import etree
from lxml import html
from lxml.html.clean import Cleaner

from zope.app.component.hooks import setSite
from zope.event import notify

from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime

from Products.Archetypes.Widget import RichWidget
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError


log = logging.getLogger('cleanWordPastedText')

def write(filename, msg): 
    f = open(filename, 'a+')
    f.write('%s' % msg.encode('ascii', 'replace'))
    f.close()
    return

def run(app, site, portal_type):
    """ """
    ll = []
    for o in queryObjs(site, portal_type, 40):
        fs = getRichTextFields(o)
        if len(fs):
            for f in fs:
                old_text = getUnicodeText(f.getAccessor(o)())
                text = old_text.replace('&lt;', '<')
                text = text.replace('&gt;', '>')
                text = text.replace('<p></p>', '')
                text = text.replace('<p>&nbsp;</p>', '')
                text = text.replace('\n', '')
                text = text.replace('\r', '')
                text.strip();
                text = sanitize(site, text, documentCleaner())
                text = text.replace('<p></p>', '').replace('<p>&nbsp;</p>', '').replace('\n', '').replace('\r', '')
                text.strip();
                assert type(text) == UnicodeType
                if old_text != text:
                    path = '/'.join(o.getPhysicalPath())
                    write('cleaned_objects.log', path+'\n')
                    write('cleaned_objects.log', old_text+'\n\n')
                    write('cleaned_objects.log', text+'\n\n')
                    log.info(path)
                    ll.append(path)
                    f.getMutator(o)(text)
                    update_version_on_edit(o)
                    
        if len(ll) and not len(ll)%1000:
            transaction.commit()
            log.info('transaction.commit(), %d' % len(ll))
    t = 'Cleaned up %d %s objects' % (len(ll), portal_type)
    write('cleaned_objects.log', t+'\n\n')
    log.info(t)

    if len(ll):
        return '%d objects affected' % len(ll)
    else:
        return '0 objects affected'

def update_version_on_edit(context):
    pr = context.portal_repository
    putils = context.plone_utils
    if pr.isVersionable(context):
        comment = 'Changed via the cleanWordPastedText.py script on %s' % DateTime()
        if (pr.supportsPolicy(context, 'at_edit_autoversion')):
            try:
                context.portal_repository.save(obj=context, comment=comment)
            except FileTooLargeToVersionError:
                putils.addPortalMessage(
                    _("Versioning for this file has been disabled because it is too large"), type="warn")
        return 'success'


def getUnicodeText(text):
    try:
        return unicode(text, 'utf-8')
    except UnicodeDedeError:
        pass

    try:
        return unicode(text, 'utf-16')
    except UnicodeDedeError:
        pass

    try:
        return unicode(text, 'cp1252')
    except UnicodeDedeError:
        pass


def queryObjs(self, portal_type, limit=-1):
    catalog = getToolByName(self, 'portal_catalog')
    if limit > 0:
        return [o.getObject() for o in catalog(portal_type=portal_type)[:limit]]
    return [o.getObject() for o in catalog(portal_type=portal_type)]

def getRichTextFields(object):
    return [f for f in object.Schema().fields()
              if isinstance(f.widget, RichWidget)]

def documentCleaner():
    return Cleaner(
                page_structure = False,
                remove_unknown_tags = False,
                safe_attrs_only = True,
                allow_tags = [ "br", "blockquote", "a", "em", "p", "strong" ],
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

try:
    site = app.osha.portal
except AttributeError:
    site = app.osha
setSite(site)
admin = app.acl_users.getUser('admin').__of__(site.acl_users)
newSecurityManager(None, admin)
portal_type = 'OSH_Link'
status = run(app, site, portal_type)
transaction.commit()
app._p_jar.sync()
