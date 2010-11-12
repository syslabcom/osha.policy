def run(self):
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

