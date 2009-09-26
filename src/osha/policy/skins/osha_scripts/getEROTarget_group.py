## Script (Python) "getEROTarget_group"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get TargetGroup Metadata
##

try:
    return context.getField('ero_target_group').getAccessor(context)() 
except:
    return ''
