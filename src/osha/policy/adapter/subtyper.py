from p4a.subtyper import interfaces
import zope.component
import zope.interface
import zope.app.content.interfaces


class IAnnotatedLinkList(zope.interface.Interface): 
    pass

class AnnotatedLinkListDescriptor(object):
    zope.interface.implements(interfaces.IPortalTypedDescriptor)
    title = u'Annotated Links'
    description = u'Annotated links can be used by portlets to display additional information'
    type_interface = IAnnotatedLinkList
    for_portal_type = 'Document'

