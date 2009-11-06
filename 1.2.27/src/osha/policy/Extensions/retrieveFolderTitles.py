def retrieveFolderTitles(self):
    """ accesses all Folders. If a folder doesn't have a title, get 
        the index page and retrieve its title 
    """
    
    pc = self.portal_catalog
    FTYPES = ['Folder', 'Large Plone Folder']
    results = pc(portal_type=FTYPES, Language='all')
    FB = []
    
    for result in results:
        if result.Title and result.Title != result.getId:
            continue
            
        ob = result.getObject()
        ip = ob.getDefaultPage()
        if not ip:
            continue
        
        ipob = getattr(ob, ip)
        iptitle = ipob.Title()
        if iptitle:        
            ob.setTitle(iptitle)
            FB.append("Set Title for %s to %s" % (result.getPath(), iptitle))        

    return "\n".join(FB)

