## Script (Python) "getCountry"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get Country Metadata
##

try:
    return context.getField('country').getAccessor(context)() 
except:
    return ''
