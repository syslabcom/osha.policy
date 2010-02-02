from AccessControl import ModuleSecurityInfo

from Products.CMFCore import DirectoryView
from Products.ATContentTypes.content.document import ATDocument

import new
import adapter
from patches import *

osha_globals= globals()

PROJECTNAME = 'OSHA 3.0'

DirectoryView.registerDirectory('skins', osha_globals)

ModuleSecurityInfo('osha.policy.utils').declarePublic('logit')
ModuleSecurityInfo('slc.cleanwordpastedtext.utils').declarePublic('update_object_history')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
