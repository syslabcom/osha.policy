from zope.component import getUtility 
from zope.formlib import form 
from plone.app.controlpanel.form import ControlPanelForm 
from osha.policy.interfaces import IDatabaseSettings 
from osha.theme import OSHAMessageFactory as _

def osha_database_settings(context): 
    return getUtility(IDatabaseSettings) 

class OSHADatabaseControlPanel(ControlPanelForm): 

    form_fields = form.FormFields(IDatabaseSettings) 
    form_name = _(u"OSHA Database settings") 
    label = _(u"OSHA Database settings") 
    description = _(u"Please enter the appropriate connection settings" 
                      "for the database") 

