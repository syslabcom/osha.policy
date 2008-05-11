from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.Archetypes.atapi import RichWidget
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.Archetypes.atapi import TextField
from Products.Archetypes.Storage import MetadataStorage
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes import PloneMessageFactory as _

# make the description field of NewsItems render HTML
description =  TextField('description',
              required=False,
              searchable=True,
              accessor="Description",
              mutator='setDescription',
              edit_accessor="getRawDescription",
              isMetadata=True,
              storage=MetadataStorage(),
              generateMode="mVc",
              validators = ('isTidyHtmlWithCleanup',),
              default_output_type = 'text/x-html-safe',
              allowable_content_type = ('text/html', 'text/x-html-safe'),
              schemata='default',
              widget = RichWidget(
                    label=_(u'label_description', default=u'Description'),
                    description=_(u'help_description',
                        default=u'A short summary of the content.'),
                    rows = 25,
                    allow_file_upload = zconf.ATDocument.allow_document_upload)
              )


del ATNewsItemSchema['description']
ATNewsItemSchema.addField(description)
ATNewsItemSchema.moveField('description', after='title')

finalizeATCTSchema(ATNewsItemSchema)

