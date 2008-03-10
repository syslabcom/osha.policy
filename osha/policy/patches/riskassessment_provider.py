from Products.RemoteProvider.content.Provider import Provider, Provider_schema

unwantedFields = ('allowDiscussion', 'language', 'providerCategory')
moveToCategorization = ('sme', 'remoteLanguage')
moveToBottom = ('creators', 'contributors', 'rights', 'effectiveDate', 'expirationDate')

for name in unwantedFields:
    if Provider_schema.get(name):
        Provider_schema[name].widget.visible['edit'] = 'invisible'
        Provider_schema[name].widget.visible['view'] = 'invisible'
        Provider_schema.changeSchemataForField(name, 'default')

for name in moveToCategorization:
    if Provider_schema.get(name):
        Provider_schema.changeSchemataForField(name, 'categorization')

for name in moveToBottom:
    if Provider_schema.get(name):
        Provider_schema.moveField(name, pos='bottom')
        #print "moved:", name
