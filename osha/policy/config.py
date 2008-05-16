# -*- coding: utf-8 -*-
#
# File: config.py


__author__ = """SYSLAB.COM <info@syslab.com>"""
__docformat__ = 'plaintext'


from Products.CMFCore.permissions import setDefaultRoles

DEFAULT_RIGHTS = "European Agency for Safety and Health at Work"
AUTHOR = "European Agency for Safety and Health at Work" # Set your default author here

PROJECTNAME = "OSHA"

DEFAULT_ADD_CONTENT_PERMISSION = "Add portal content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

product_globals = globals()

