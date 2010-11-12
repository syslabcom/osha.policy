def removeSEPKeywords(self):
    """ Some SEPs still have a keyword property set on them.
        Look for them, set the prop as the SEP's subject and remove the 
        prop.
    """
    logdict = {}
    seps = self.portal_catalog(
                object_provides='osha.policy.interfaces.ISingleEntryPoint',
                review_state="published"
                )
    for sep in seps:
        sep = sep.getObject()
        kw = sep.getProperty('keyword')
        if not kw:
            continue
        sep._delProperty('keyword')
        logdict['/'.join(sep.getPhysicalPath())] = kw
        subjects = sep.Subject()
        if kw in subjects:
            continue 
        subjects += (kw,)
        sep.setSubject(subjects)

    return logdict or 'None'

def copyDefaultViewCategory(self):
    """ Some SEPs don't actually have a category ('subject') set. Instead, it's
        on their index_html pages. This method copies them over to the SEP as well.
    """ 
    seps_set = []
    seps = self.portal_catalog(
                object_provides='osha.policy.interfaces.ISingleEntryPoint',
                review_state="published"
                )
    for sep in seps:
        sep = sep.getObject()
        sep_subjects = sep.Subject()
        if sep_subjects:
            continue
        try:
            page = sep._getOb(sep.getDefaultPage())
        except:
            continue
        page_subjects = page.Subject()
        if not page_subjects:
            continue

        sep.setSubject(page_subjects)
        seps_set.append('/'.join(sep.getPhysicalPath()))

    return seps_set or 'None'

