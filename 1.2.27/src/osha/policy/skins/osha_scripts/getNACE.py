## Script (Python) "getNACE"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get OSHA Nace Metadata
##


try:
    return context.getField('nace').getAccessor(context)() 
except:
    return []
