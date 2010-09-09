from slc.seminarportal.browser.seminar_view import SeminarView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Acquisition import *


class SpeakerView(SeminarView):
    """Override speech view so that we can hook our check for eliminating
    translations of speeches"""

    template = ViewPageTemplateFile('templates/speaker_view.pt')

    def __call__(self, *args, **kw):

        obj = self.context
        speeches = obj.getSpeeches()
        valid = list(set([x.getCanonical().UID() for x in speeches]))
        obj.setSpeeches(valid)
        return self.template()
