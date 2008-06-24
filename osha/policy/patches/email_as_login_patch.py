from Products.CMFPlone.MembershipTool import MembershipTool
from Products.CMFPlone.RegistrationTool import RegistrationTool
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

    
def email_mailPassword(self, email, REQUEST):
    """ Wrapper around mailPassword """
    import pdb;pdb.set_trace()
    registration = getToolByName(self, 'portal_registration')

    forgotten_userid = ''
    luf=getLDAPPlugin()._getLDAPUserFolder()
    result = luf._lookupuserbyattr('mail', email)
    if len(result)>3:
        attrs = result[2]
        try:
            forgotten_userid = attrs.get('uid')[0]
        except:
            pass
        
    
    registration.mailPassword(forgotten_userid, REQUEST)

RegistrationTool.email_mailPassword = email_mailPassword
