from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.GenericSetup import EXTENSION, profile_registry
from Products.CMFCore import DirectoryView

from Products.ATContentTypes.content.document import ATDocument
import new

from zLOG import LOG, INFO
osha_globals= globals()

PROJECTNAME = 'OSHA 3.0'
def log(msg):
    LOG(PROJECTNAME, INFO, msg)

import adapter

from patches import linguaplone_addTranslation_patch

# Enable getTranslation caching for LinguaPlone
#from Products.LinguaPlone import config
#config.CACHE_TRANSLATIONS = 1
#CACHE_TRANSLATIONS = 1

DirectoryView.registerDirectory('skins', osha_globals)

from AccessControl import ModuleSecurityInfo
ModuleSecurityInfo('Products.OSHA.utils').declarePublic('logit')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""


