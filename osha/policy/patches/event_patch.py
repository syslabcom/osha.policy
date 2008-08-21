from Products.ATContentTypes.content.event import ATEventSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema


# Add the subject field again
ATEventSchema['subject'].widget.visible = {'edit': 'visible'}
ATEventSchema['subject'].mode = 'rw'

finalizeATCTSchema(ATEventSchema)

