## Script (Python) "getEROTopic"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get Topic Metadata
##

try:
    return context.getField('ero_topic').getAccessor(context)() 
except:
    return ''
