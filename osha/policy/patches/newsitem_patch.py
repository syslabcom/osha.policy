from Products.ATContentTypes.content.newsitem import ATNewsItemSchema
from Products.Archetypes.atapi import RichWidget
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes import PloneMessageFactory as _

# make the description field of NewsItems render HTML

ATNewsItemSchema['description'].default_output_type = 'text/html'
ATNewsItemSchema['description'].default_content_type = 'text/html'
ATNewsItemSchema['description'].widget = RichWidget(
            label=_(u'label_description', default=u'Description'),
            description=_(u'help_description',
                              default=u'A short summary of the content.'),
            rows = 25,
            allow_file_upload = zconf.ATDocument.allow_document_upload,
            )
