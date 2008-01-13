## Script (Python) "getCountry"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get OSHA Country Metadata
##

try:
    return container.portal_annotatablemetadata.getValue(context, 'Country')
except:
    return []
