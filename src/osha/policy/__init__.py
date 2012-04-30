from AccessControl import ModuleSecurityInfo
from Products.CMFCore import DirectoryView
from patches import *

osha_globals = globals()

PROJECTNAME = 'OSHA 3.0'

DirectoryView.registerDirectory('skins', osha_globals)

ModuleSecurityInfo('osha.policy.utils').declarePublic('logit')
ModuleSecurityInfo('slc.cleanwordpastedtext.utils').declarePublic(
    'update_object_history')
ModuleSecurityInfo('slc.alertservice.utils').declarePublic(
    'encodeEmail')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    from AccessControl import allow_module
    allow_module('slc.alertservice')
