from Products.CMFPlone.MembershipTool import MembershipTool

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