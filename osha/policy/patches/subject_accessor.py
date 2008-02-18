
from Products.OSHContentLink.OSH_Link import OSH_Link
from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink
from Products.RemoteProvider.content.Provider import Provider
from Products.CaseStudy.CaseStudy import CaseStudy

def getSubject(self):
    """ Very specific osha getter. We want to make sure that the toplevel cats always represent the subject
    """
    subcats = self.getField('subcategory').getAccessor(self)()
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

RiskAssessmentLink.getSubject = getSubject
RiskAssessmentLink.Subject = Subject

Provider.getSubject = getSubject
Provider.Subject = Subject

CaseStudy.getSubject = getSubject
CaseStudy.Subject = Subject