
from Products.OSHContentLink.OSH_Link import OSH_Link
from Products.RALink.content.RALink import RALink
from Products.RemoteProvider.content.Provider import Provider
from Products.CaseStudy.CaseStudy import CaseStudy
from Products.ATContentTypes.content.file import ATFile
from plone.app.blob.content import ATBlob
from Products.ATContentTypes.content.event import ATEvent

def getSubject(self):
    """ Very specific osha getter. We want to make sure that the toplevel cats always represent the subject
    """
    subcats = self.getField('subcategory')
    if subcats is  None:
        return tuple()
    subcats = subcats.getAccessor(self)()
    # XXX: Bad hack but works. I take all keys which have no :: inside
    subjects = {}
    for subcat in subcats:
        if subcat.find('::')==-1:
            subjects[subcat] = 1
        else:
            elems = subcat.split("::")
            subjects[elems[0]] = 1
    return subjects.keys()

def Subject(self):
    """ alias to getSubject """
    return self.getSubject()
    
    

OSH_Link.getSubject = getSubject
OSH_Link.Subject = Subject

#RALink.getSubject = getSubject
#RALink.Subject = Subject

Provider.getSubject = getSubject
Provider.Subject = Subject

ATFile.getSubject = getSubject
ATFile.Subject = Subject

ATBlob.getSubject = getSubject
ATBlob.Subject = Subject

ATEvent.getSubject = getSubject
ATEvent.Subject = Subject

# There are no longer subcategories on CaseStudies
#CaseStudy.getSubject = getSubject
#CaseStudy.Subject = Subject