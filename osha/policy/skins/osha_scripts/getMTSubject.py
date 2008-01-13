## Script (Python) "getMTSubject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get OSHA MTSubject Metadata
##

try:
    return container.portal_annotatablemetadata.getValue(context, 'MultilingualThesaurus')
except:
    return []
