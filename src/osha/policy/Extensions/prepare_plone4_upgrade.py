import Acquisition
from logging import getLogger
from zope.component.interfaces import ComponentLookupError
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces._content import IFolderish
from Products.CMFPlone.utils import getSiteEncoding
from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY, USER_CATEGORY
import transaction
from zope.component import getUtility

# interface import, needed for removal
from plone.portlets.interfaces import IPortletManager

logger = getLogger('osha.policy/prepare_plone4_upgrade')

br = '<br />'
link = '<a href="%(url)s">%(text)s</a>' + br

class LogWriter(object):

    def __init__(self, response=None):
        self.response = response

    def write(self, msg):
        if self.response:
            if isinstance(msg, unicode):
                msg = msg.encode(getSiteEncoding(self))
            self.response.write(msg + br)
        logger.info(msg)

def setup_log(self, response):
    log = LogWriter(response)
    if response:
        response.setHeader('Content-Type', 'text/html;charset=UTF-8')
        response.setHeader('Expires', 'Sat, 1 Jan 2000 00:00:00 GMT')
        response.setHeader('Pragma', 'no-cache')
        self.backlink = link % dict(
            url=self.absolute_url() + '/manage_workspace', text='Back to ZMI')
        response.write('<html><body>')
        response.write(self.backlink)
        response.write(br)
    return log

def setup(self, log):
    pname = self.Title()
    if not isinstance(pname, unicode):
        pname = pname.decode('utf-8')
    pid = self.getId()
    log.write(u'<h2>Preparing %s (%s) ...</h2>' % (pname, pid))
    if not self or self.portal_type != 'Plone Site':
        log.write(u'%s is not a Plone Site' % pname)
        finish(self, response)
        return

def finish(self, response):
    if response:
        response.write(br)
        response.write(self.backlink)

def uninstall_interfaces(self, log):
    try:
        view = self.restrictedTraverse('@@fix-persistent-utilities')
    except:
        log.write(
            u'<p style="color: red">ERROR: it seems the package wildcard.'
            'fixpersistentutilities is not installed. Please add it to your '
            'buildout!')
        return
    log.write(
        '<h2>Removing unwanted persistent utilities</h2><p>(Courtesy of '
        'wildcard.fixpersistentutilities)</p>')

    view.activate_expert_mode()
    # keys: provided, adapter, subscribers
    ut = view.utilities()
    ad = ut['adapters']
    sub = ut['subscribers']
    # IPortletManager
    adapter = IPortletManager
    reg = ad.get(adapter)
    names = ['osha.abovecontent.portlets', 'osha.belowcontent.portlets']

    for name in names:
        util = reg.get(name)
        if util:
            msg = "remove adaper %s for %s" % (name, str(adapter))
            msg = msg.replace('<', '&lt;')
            log.write(msg)
            params = view.utility_reg_data(adapter, 'adapters', name, util)
            view.request.set('submit', 1)

            for k,v  in params.items():
                view.request.set(k, v)
            view.delete_utility_reg()

    sub_reg = sub.get(adapter)
    # the subscribers are found under key ''
    key = u''
    subscribers = sub_reg.get(key)
    for subscriber in subscribers:
        if subscriber.__name__ in names:
            msg = "remove subscriber %s for %s" % (
                subscriber.__name__, str(adapter))
            msg = msg.replace('<', '&lt;')
            log.write(msg)
            print "bingo"
            view.request.set('submit', 1)
            params = view.utility_reg_data(
                adapter, 'subscribers', key, subscriber)
            for k,v  in params.items():
                view.request.set(k, v)
            view.delete_utility_reg()

    # Now for the interfaces
    view = self.restrictedTraverse('@@fix-interfaces-fpu')
    iface_names = ['osha.theme.browser.interfaces.IOSHABelowContent',
        'osha.theme.browser.interfaces.IOSHAAboveContent']
    view.request.set('submitted', 1)
    for name in iface_names:
        view.request.set('dottedname', name)
        log.write('remove interface %s' % name)
        view()

def remove_portlets(portal, log):
    log.write('<h3>Remove unwanted portlets</h3>')
    ltool = getToolByName(portal, 'portal_languages')
    langs = ltool.getSupportedLanguages()
    portlets_to_remove = ['partners']

    def doRemoval(obj):
        path = '/'.join(obj.getPhysicalPath())
        try:
            left = assignment_mapping_from_key(
                obj, 'plone.leftcolumn', CONTEXT_CATEGORY, path)
            right = assignment_mapping_from_key(
                obj, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
        except ComponentLookupError:
            return
        lportlets = [x for x in list(left.keys())]
        rportlets = [x for x in list(right.keys())]

        for name in lportlets:
            if name in portlets_to_remove:
                log.write(
                    'Removed %s from left slot of %s' % (
                        name, obj.absolute_url()))
                del left[name]
        for name in rportlets:
            if name in portlets_to_remove:
                log.write(
                    'Removed %s from right slot of %s' % (
                        name, obj.absolute_url()))
                del right[name]


    def doRecursion(obj):
        for subobj in obj.objectValues():
            doRemoval(subobj)
            if IFolderish.providedBy(subobj):
                doRecursion(subobj)

    for lang in langs:
        if not hasattr(Acquisition.aq_base(portal), lang):
            continue
        log.write("<strong>handling language '%s'</strong>" %lang)
        F = getattr(portal, lang)
        doRemoval(F)
        doRecursion(F)

    dashboards = [
        getUtility(IPortletManager, name=name) for name in
        ['plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3',
         'plone.dashboard4']]

    to_remove = [
        'help', 'help-1', 'help-2', 'support', 'support-1', 'my-teams',
        'my-teams-1', 'test-the-system', 'test-the-system-1']
    for userid in portal.Members.objectIds('ATFolder'):
        for dashboard in dashboards:
            try:
                dashmapping = assignment_mapping_from_key(
                    portal, dashboard.__name__, USER_CATEGORY, key=userid)
                dashportlets = [x for x in dashmapping.keys()]
                for name in dashportlets:
                    if name in to_remove:
                        del dashmapping[name]
                        log.write(
                            'Removed %s from %s for user %s' %(
                                name, dashboard.__name__, userid))
                dashportlets = [
                    x for x in dashboard.get(
                        USER_CATEGORY, {}).get(userid, {}).keys()]
                print dashboard, dashportlets


def fix_miscellaneous(portal, log):
    log.write('<h3>Fix miscellaneous</h3>')
    path = "de/index_foursteps"
    obj = portal.restrictedTraverse(path)
    for ob in obj.getTranslations().values():
        text = ob[0].getText().replace("&quot;", "'")
        ob[0].setText(text)
        log.write('Replaced quot with single quotation mark on index_foursteps')

def uninstall_products(self, log):
    uninst_products = ['FCKeditor',
                       'p4a.plonevideo',
                       'p4a.plonevideoembed',
                       'p4a.video',
                       'p4a.ploneaudio',
                       'p4a.audio',
                       'CacheSetup',
                       'dateable.chronos',
                       'p4a.plonecalendar',
                       'simplon.plone.ldap',
                       'osha.policy',
                       'osha.theme',
                       'osha.adaptation',
                       'osha.legislation',
                       'webcouturier.dropdownmenu',
#                       'Products.VocabularyPickerWidget',
                       ]

    qi = getToolByName(self, 'portal_quickinstaller')
    log.write(u'<h3>Uninstalling products</h3>')
    for prod in uninst_products:
        if qi.isProductInstalled(prod):
            if len(qi[prod].utilities) > 3:
                log.write(
                    u'Suspiciously many (%i) utilities registered for %s!' % (
                        len(qi[prod].utilities), prod))
            try:
                out = qi.uninstallProducts(products=[prod])
            except Exception, ex:
                out = 'ERROR while uninstalling %s: %s: %s' % (
                    prod, ex.__class__.__name__, ex)
            out = u'%s uninstalled (output: %s)' % (prod,out)
            log.write(u'  ' + out)
        # else:
        #     log.write(u'  %s not installed, skipped' % prod)

def delete_proxy_indexes(self, log):
    cat = getToolByName(self, 'portal_catalog_real')
    log.write(u'<h3>Deleting ProxyIndexes</h3>')
    indexes = cat.index_objects()
    idx_to_delete = [
        idx.getId() for idx in indexes if idx.meta_type == 'ProxyIndex']
    for id in idx_to_delete:
        cat.manage_delIndex(id)
        log.write(u'\tDeleted %s' % id)
    log.write('<h3>Emptying catalog</h3>')
    cat.manage_catalogClear()

def remove_ldap_plugin(self):
    log.write('Deleting the LDAP plugin in the acl_users folder')
    pas = getToolByName(self, 'acl_users')
    id = 'ldap'
    if id in pas.objectIds():
        pas.manage_delObjects(id)

def prepare_plone4_upgrade(self, REQUEST=None):
    """ Prepares an existing Plone 3 portal for upgrade to Plone 4. Needs to be
        run on the Plone 3 instance before the Data.fs can be used by Plone 4.
    """
    response = self.REQUEST and self.REQUEST.RESPONSE or None
    log = setup_log(self, response)
    setup(self, log)

    # uninstall_products(self, log) 
    # delete_proxy_indexes(self)

    # remove_ldap_plugin(self)

    ## apparently, not needed!
    ## uninstallInterfaces(self, log)

    remove_portlets(self, log)
    # fix_miscellaneous(self, log)

    log.write(u"<p><em>Finished, all is well</em></p>")
    finish(self, response)
