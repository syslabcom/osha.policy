from Products.CMFCore.utils import getToolByName

def notifyMemberAreaCreated(self, **args):
    pm = getToolByName(self, 'portal_membership')
    hf = pm.getHomeFolder()

    if hf is not None:
        defaultTypes = [x.getId() for x in  hf.getDefaultAddableTypes()]
        immediatelyAddable = [ 'Provider'
                             , 'OSH_Link'
                             , 'RALink'
                             , 'CaseStudy'
                             , 'Folder'
                             , 'RichDocument']
        # Specify types manually
        hf.setConstrainTypesMode(1)
        # All types should be allowed
        hf.setLocallyAllowedTypes(defaultTypes)
        # But only some are visible in the drop-down
        hf.setImmediatelyAddableTypes(immediatelyAddable)
