from Products.LinguaPlone.utils import generateMethods


from osha.legislation.content.directive import DirectiveSchema, Directive
from osha.legislation.content.amendment import AmendmentSchema, Amendment
from osha.legislation.content.modification import ModificationSchema, Modification
from osha.legislation.content.note import NoteSchema, Note
from osha.legislation.content.proposal import ProposalSchema, Proposal

from osha.whoswho.content.whoswho import whoswhoSchema, whoswho

from Products.CallForContractors.CallForContractors import CallForContractors_schema, CallForContractors
from Products.CaseStudy.CaseStudy import CaseStudy_schema, CaseStudy
from Products.PublicJobVacancy.PublicJobVacancy import PublicJobVacancy_schema, PublicJobVacancy
from Products.RemoteProvider.content.Provider import Provider_schema, Provider

from Products.ATContentTypes.content.event import ATEventSchema, ATEvent
from Products.ATContentTypes.content.file import ATFileSchema, ATFile
from Products.ATContentTypes.content.image import ATImageSchema, ATImage
from Products.ATContentTypes.content.folder import ATFolderSchema, ATFolder
from Products.ATContentTypes.content.folder import ATBTreeFolderSchema, ATBTreeFolder
from Products.ATContentTypes.content.link import ATLinkSchema, ATLink
from Products.ATContentTypes.content.topic import ATTopicSchema, ATTopic
from Products.ATContentTypes.content.newsitem import ATNewsItemSchema, ATNewsItem
from Products.ATContentTypes.content.document import ATDocumentSchema, ATDocument

from plone.app.blob.content import ATBlobSchema, ATBlob

from Products.RichDocument.content.richdocument import RichDocumentSchema, RichDocument

from Products.RALink.content.RALink import RALink_schema, RALink
from Products.RiskAssessmentLink.content.RiskAssessmentLink import RiskAssessmentLink_schema, RiskAssessmentLink

patchpairs = [
    (DirectiveSchema, Directive),
    (AmendmentSchema, Amendment),
    (ModificationSchema,Modification),
    (NoteSchema,Note),
    (ProposalSchema,Proposal),
    (whoswhoSchema,whoswho),
    (CallForContractors_schema,CallForContractors),
    (CaseStudy_schema,CaseStudy),
    (PublicJobVacancy_schema, PublicJobVacancy),
    (Provider_schema, Provider),
    (ATEventSchema, ATEvent),
    (ATFileSchema, ATFile),
    (ATImageSchema, ATImage),
    (ATFolderSchema, ATFolder),
    (ATBTreeFolderSchema, ATBTreeFolder),
    (ATLinkSchema, ATLink),
    (ATTopicSchema, ATTopic),
    (ATNewsItemSchema, ATNewsItem),
    (ATDocumentSchema, ATDocument),
    (ATBlobSchema, ATBlob),
    (RichDocumentSchema, RichDocument),
    (RALink_schema, RALink),
    (RiskAssessmentLink_schema, RiskAssessmentLink)
]


from osha.policy.adapter.schemaextender import LANGUAGE_INDEPENDENT_INITIALIZED

#import pdb; pdb.set_trace()

for pair in patchpairs:
    print pair
    schema = pair[0]
    klass = pair[1]

    schema['subject'].languageIndependent = True
    if not getattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, False):
        generateMethods(klass, [schema['subject']])
        print "called generateMethods for subject on ", klass
        setattr(klass, LANGUAGE_INDEPENDENT_INITIALIZED, True)
