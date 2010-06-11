
from Products.OSHContentLink.OSH_Link import OSH_Link
from Products.RALink.content.RALink import RALink
from Products.RemoteProvider.content.Provider import Provider
from Products.CaseStudy.CaseStudy import CaseStudy
from Products.ATContentTypes.content.file import ATFile
from plone.app.blob.content import ATBlob
from Products.ATContentTypes.content.event import ATEvent
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.link import ATLink
from Products.PloneHelpCenter.content.FAQ import HelpCenterFAQ

def getSubject(self):
    """ Very specific osha getter. We want to make sure that the toplevel cats always represent the subject
    """
    subcats = self.getField('subcategory')
    if subcats is None:
        return self._old_subject()
    subcats = subcats.getAccessor(self)()
    # XXX: Bad hack but works. I take all keys which have no :: inside
    subjects = {}
    for subcat in subcats:
        if subcat.find('::')==-1:
            subjects[subcat] = 1
        else:
            elems = subcat.split("::")
            subjects[elems[0]] = 1
    # original Subject, if available
    origsub = set(self._md.get('subject', []))
    all_subs = origsub.union(subjects.keys())
    return list(all_subs)

def Subject(self):
    """ alias to getSubject """
    return self.getSubject()



OSH_Link._old_subject = OSH_Link.Subject
OSH_Link.getSubject = getSubject
OSH_Link.Subject = Subject

RALink._old_subject = RALink.Subject
RALink.getSubject = getSubject
RALink.Subject = Subject

Provider._old_subject = Provider.Subject
Provider.getSubject = getSubject
Provider.Subject = Subject

ATFile._old_subject = ATFile.Subject
ATFile.getSubject = getSubject
ATFile.Subject = Subject

ATBlob._old_subject = ATBlob.Subject
ATBlob.getSubject = getSubject
ATBlob.Subject = Subject

ATEvent._old_subject = ATEvent.Subject
ATEvent.getSubject = getSubject
ATEvent.Subject = Subject

ATImage._old_subject = ATImage.Subject
ATImage.getSubject = getSubject
ATImage.Subject = Subject

ATLink._old_subject = ATLink.Subject
ATLink.getSubject = getSubject
ATLink.Subject = Subject

CaseStudy._old_subject = CaseStudy.Subject
CaseStudy.getSubject = getSubject
CaseStudy.Subject = Subject

HelpCenterFAQ.getSubject = getSubject
HelpCenterFAQ.Subject = Subject
