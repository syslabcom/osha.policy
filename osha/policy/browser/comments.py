import logging

from Acquisition import aq_inner
from Acquisition import Implicit
from AccessControl import getSecurityManager

from zope.interface import implements

from plone.app.layout.viewlets import comments
from plone.app.kss.interfaces import IPloneKSSView
from plone.app.kss.plonekssview import PloneKSSView

from kss.core import force_unicode

from Products.CMFPlone.utils import IndexIterator
from Products.CMFPlone.utils import getToolByName
from Products.CMFPlone import MessageFactory
from Products.CMFFormController.ControllerState import ControllerState
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.qPloneComments.utils import manage_mails

from interfaces import IReportAbuse
qpcMF = MessageFactory('plonecomments')

log = logging.getLogger('osha.policy.browser.comments.py')


class CommentsViewlet(comments.CommentsViewlet):
    """A custom version of the comments viewlet
    """

    render = ViewPageTemplateFile('templates/comments.pt')

    def is_moderation_enabled(self):
        """ Returns a boolean indicating whether the user has enabled moderation
            in the qPloneComments configlet
        """
        portal_properties = getToolByName(self.context, 'portal_properties')
        try:
            return portal_properties.qPloneComments.getProperty('enable_moderation', None)
        except AttributeError:
            return False

    def can_moderate(self):
        """ Returns a boolean indicating whether the user has the 'Moderate Discussion'
            permission
        """
        return getSecurityManager().checkPermission('Moderate Discussion', aq_inner(self.context))


class utils(BrowserView):
    """ """
    implements(IReportAbuse)

    def report_abuse(self):
        """ Report Abuse
        """
        context = self.context
        manage_mails(context, context, 'deleting')

        parent = context.inReplyTo()
        if parent is not None:
            talkback = context.portal_discussion.getDiscussionFor(parent)
        else:
            talkback = context.aq_parent

        # redirect to the object that is being discussed
        redirect_target = context.plone_utils.getDiscussionThread(talkback)[0]
        view = redirect_target.getTypeInfo().immediate_view
        context.plone_utils.addPortalMessage(qpcMF(u'Abuse Reported.'))
        context.REQUEST['RESPONSE'].redirect( redirect_target.absolute_url() + '/%s' % view )

    def email_from_address(self):
        """ """
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        return portal.email_from_address

    def member(self):
        """ """
        pm = getToolByName(self.context, 'portal_membership')
        return pm.getAuthenticatedMember()

    def report_abuse_enabled(self):
        """ """
        prop_sheet = self.context.portal_properties['qPloneComments']
        value =  prop_sheet.getProperty('enable_report_abuse', False)
        log.info('enable_report_abuse: %s' % value)
        return value

    def tabindex(self):
        """ Needed for BBB, tabindex has been deprecated.
        """
        return IndexIterator()

    def portal_url(self):
        """ """
        return getToolByName(self.context, 'portal_url')


class MixinKSSView(Implicit, PloneKSSView):
    implements(IPloneKSSView)

    def macroContent(self, macropath, **kw):
        """ Renders a macro and returns its text 
            Customization of plone/app/kss/plonekssview.py macroContent to allow
            browser view template macros to be rendered as well.
        """
        path = macropath.split('/')
        if len(path) < 2 or path[-2] != 'macros':
            raise RuntimeError, 'Path must end with macros/name_of_macro (%s)' % (repr(macropath), )
        # needs string, do not tolerate unicode (causes but at traverse)
        jointpath = '/'.join(path[:-2]).encode('ascii')
        macroobj = self.context.restrictedTraverse(jointpath)
        try:
            the_macro = macroobj.macros[path[-1]]
        except  AttributeError:
            # XXX: My customization, the only way I could get macros 
            # of browser templates to render. - JC Brand
            the_macro = macroobj.index.macros[path[-1]]
        except IndexError:
            raise RuntimeError, 'Macro not found'

        # put parameters on the request, by saving the original context
        self.request.form, orig_form = kw, self.request.form
        content = self.header_macros.__of__(macroobj.aq_parent)(the_macro=the_macro)
        self.request.form = orig_form
        # Always encoded as utf-8
        content = force_unicode(content, 'utf')
        return content


class CommentsKSS(MixinKSSView):
    """ Operations on the report abuse form using KSS.
    """   

    def submit_abuse_report(self, comment_id):
        """ """
        errors = {}
        context = aq_inner(self.context)
        request = context.REQUEST
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if hasattr(context, 'captcha_validator'):
            dummy_controller_state = ControllerState(
                                            id='comments.pt',
                                            context=context,
                                            button='submit',
                                            status='success',
                                            errors={},
                                            next_action=None,)
            # get the form controller
            controller = portal.portal_form_controller
            # send the validate script to the form controller with the dummy state object
            controller_state = controller.validate(dummy_controller_state, request, ['captcha_validator',])
            errors.update(controller_state.errors)

        message = request.get('message')
        if not message:
            errors.update({'message': 'Please provide a message'})

        ksscore = self.getCommandSet('core')
        if errors:
            html = self.macroContent('@@report-abuse-form/macros/form',
                                     errors=errors,
                                     show_form=True,
                                     tabindex=IndexIterator(),
                                     **request.form)
            ksscore.replaceInnerHTML(
                            ksscore.getHtmlIdSelector('span-reply-form-holder-%s' % comment_id), 
                            html)
            return self.render()

        pd = self.portal_discussion
        dl = pd.getDiscussionFor(context)
        comment = dl._container.get(comment_id)
        report_abuse(context, context, message, comment)
        html = self.macroContent('@@report-abuse-form/macros/form',
                                 tabindex=IndexIterator(),
                                 **request.form)
        node = ksscore.getHtmlIdSelector('span-reply-form-holder-%s' % comment_id)
        ksscore.replaceInnerHTML(node, html)
        ksscore.insertHTMLAsLastChild(
            node,
            '<br/> <strong style="color:red">This comment has been reported for abuse.</strong>')
        return self.render()


def report_abuse(reply, context, message, comment):

    def getParent(reply):
        if reply.meta_type == 'Discussion Item':
            reply = reply.inReplyTo()
            return getParent(reply)
        return reply

    def getParentOwnerEmail(reply, context):
        creator_id = getParent(reply).getOwnerTuple()[1]
        creator = getToolByName(context, 'portal_membership').getMemberById(creator_id)
        allow_email = getattr(context, 'emailCommentNotification', True)
        if callable(allow_email):
            allow_email= allow_email(reply=reply, state='report_comment_abuse', creator=creator)
        if creator and allow_email:
            return creator.getProperty('email', '')
        return ''

    def getProp(self, prop_name, marker=None):
        result = marker
        pp = getToolByName(self, 'portal_properties')
        config_ps = getattr(pp, 'qPloneComments', None)
        if config_ps:
            result =  getattr(config_ps, prop_name, marker)
        return result

    user_email = getProp(context, "email_discussion_manager", None)
    if not user_email:
        return 

    reply_parent = getParent(reply)
    organization_name = getProp(context, 'email_subject_prefix', '')
    admin_email = context.portal_url.getPortalObject().getProperty('email_from_address')
    creator_name = reply.getOwnerTuple()[1]
    subject = '[%s] A comment on "%s" has been reported for abuse.' % (organization_name, getParent(context).Title())
    args={'mto': user_email,
            'mfrom': admin_email,
            'obj': reply_parent,
            'comment_id':comment.id,
            'comment_desc':comment.description,
            'comment_text':comment.text,
            'message':message,
            'organization_name': organization_name,
            'name': creator_name,
            }
    msg = getattr(context, 'report_comment_abuse_email_template')(**args)
    site_props = context.portal_properties.site_properties
    host = context.plone_utils.getMailHost()
    host.secureSend(msg, user_email, admin_email,
                    subject = subject,
                    subtype = 'plain',
                    debug = False,
                    charset = site_props.getProperty('default_charset', 'utf-8'),
                    From = admin_email)


