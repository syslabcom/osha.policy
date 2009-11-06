## Script (Python) "getHtml_meta_keywords"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=get OSHA Country Metadata
##


try:
    return container.portal_annotatablemetadata.getValue(context, 'html_meta_keywords')
except:
    return []
