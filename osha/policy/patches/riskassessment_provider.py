from Products.RemoteProvider.content.Provider import Provider, Provider_schema

unwantedFields = ('allowDiscussion', 'language', 'sme', 'subject')
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
