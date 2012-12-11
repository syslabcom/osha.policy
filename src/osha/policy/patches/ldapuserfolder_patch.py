from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder


def _mapRoles(self, groups):
    """ Perform the mapping of LDAP groups to Zope roles """
    mappings = getattr(self, '_groups_mappings', {})
    roles = []

    if getattr(self, '_implicit_mapping', None):
        # XXX patch: Make sure we get a list, so that we can append to it
        roles = [x for x in groups]

    for group in groups:
        mapped_role = mappings.get(group, None)
        if mapped_role is not None and mapped_role not in roles:
            roles.append(mapped_role)

    return roles

LDAPUserFolder._mapRoles = _mapRoles
