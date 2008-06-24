from Products.CMFPlone.MembershipTool import MembershipTool
from Products.CMFPlone.RegistrationTool import RegistrationTool
from Products.PasswordResetTool.PasswordResetTool import PasswordResetTool
from simplon.plone.ldap.ploneldap.util import getLDAPPlugin
from Products.CMFCore.utils import getToolByName

def testCurrentPassword(self, password):
    """ test to see if password is current """
    REQUEST=getattr(self, 'REQUEST', {})
    userid=self.getAuthenticatedMember().getUserId()
    acl_users = self._findUsersAclHome(userid)
    if not acl_users:
        return 0
    # also get email because we authenticate the user by email
    email=self.getAuthenticatedMember().getProperty('email')
    #return acl_users.authenticate(userid, password, REQUEST)
    return acl_users.authenticate(email, password, REQUEST)
    
MembershipTool.testCurrentPassword = testCurrentPassword

def _get_userid_by_email(self, email):
    uid = ''
    luf=getLDAPPlugin()._getLDAPUserFolder()
    result = luf._lookupuserbyattr('mail', email)
    if len(result)>3:
        attrs = result[2]
        try:
            uid = attrs.get('uid')[0]
        except:
            pass
    return uid

def email_mailPassword(self, email, REQUEST):
    """ Wrapper around mailPassword """
    registration = getToolByName(self, 'portal_registration')
    forgotten_userid = _get_userid_by_email(self, email)
    registration.mailPassword(forgotten_userid, REQUEST)

RegistrationTool.email_mailPassword = email_mailPassword

def email_resetPassword(self, email, randomstring, password):
    userid = _get_userid_by_email(self, email)
    pwreset = getToolByName(self, 'portal_password_reset')
    pwreset.resetPassword(userid, randomstring, password)

PasswordResetTool.email_resetPassword = email_resetPassword