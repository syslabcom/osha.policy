from Products.ATContentTypes.content.event import ATEvent, ATEventSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from types import StringType

# Hide the Event Type field
ATEventSchema['eventType'].widget.visible = {'edit': 'invisible'}
ATEventSchema['eventType'].mode = 'r'

# Add the subject field again
ATEventSchema['subject'].widget.visible = {'edit': 'visible'}
ATEventSchema['subject'].mode = 'rw'

finalizeATCTSchema(ATEventSchema)


def _setEventType(self, value, alreadySet=False, **kw):
    """CMF compatibility method
    DO NOT set the subject based on eventType
    """
    if type(value) is StringType:
        value = (value,)
    elif not value:
        # mostly harmless?
        value = ()
    f = self.getField('eventType')
    f.set(self, value, **kw) # set is ok


ATEvent.setEventType = _setEventType
