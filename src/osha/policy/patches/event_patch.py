from Products.ATContentTypes.content.event import ATEvent
from types import StringType

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
