from Products.RemoteProvider.content.Provider import Provider, Provider_schema

unwantedFields = ( 'subject',  'allowDiscussion', 'creation_date', 
        'modification_date', 'language', 'sme', 'provider')
moveToDefault = ['remoteLanguage', 'location', 'effectiveDate', 'expirationDate']
moveToBottom = ('creators', 'contributors', 'rights', )

for name in unwantedFields:
    if Provider_schema.get(name):
        Provider_schema[name].widget.visible['edit'] = 'invisible'
        Provider_schema[name].widget.visible['view'] = 'invisible'
        Provider_schema.changeSchemataForField(name, 'default')

for name in moveToDefault:
    if Provider_schema.get(name):
        Provider_schema.changeSchemataForField(name, 'default')

for name in moveToBottom:
    if Provider_schema.get(name):
        Provider_schema.moveField(name, pos='bottom')

# make providerCategory required
Provider_schema['providerCategory'].required = True
