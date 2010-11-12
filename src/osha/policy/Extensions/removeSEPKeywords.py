from zope.component import getMultiAdapter

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
    import pdb; pdb.set_trace()
    for sep in seps:
        sep = sep.getObject()
        kw = sep.getProperty('keyword')
        if not kw:
            continue
        sep.delProperty('keyword')
        subjects = sep.Subject()
        if kw in subjects:
            continue 
        subjects += (kw,)
        sep.setSubject(subjects)
        logdict['/'.sep.getPhysicalPath()] = kw

    return logdict

