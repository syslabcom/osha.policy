from Products.LDAPMultiPlugins.LDAPPluginBase import LDAPPluginBase


def authenticateCredentials(self, credentials):
    """ Fulfill AuthenticationPlugin requirements

    REASON FOR THE PATCH:
    Our login attribute as the user's email address, but for historical
    reasons, we also have the userId attribute.
    Therefore, if the user lookup fails, try again, this time explicitly
    using the uer's email address

    """
    acl = self._getLDAPUserFolder()
    login = credentials.get('login')
    password = credentials.get('password')

    if not acl or not login or not password:
        return None, None

    user = acl.getUser(login, pwd=password)

    if user is None:
        ploneuser = self.getUserById(login)
        if ploneuser is not None:
            mail = ploneuser.getProperty('email', None)
            if mail is not None:
                user = acl.getUser(mail, pwd=password)
                if user is None:
                    return (None, None)
            else:
                return (None, None)
        else:
            return (None, None)

    return (user.getId(), user.getUserName())

LDAPPluginBase.authenticateCredentials = authenticateCredentials
