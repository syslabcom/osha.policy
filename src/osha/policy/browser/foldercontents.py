from Acquisition import aq_inner
from Products.ATContentTypes.interface import IATTopic
from Products.Archetypes.interfaces import ISchema
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.app.content.browser.foldercontents import FolderContentsView, \
    FolderContentsTable
from plone.app.content.batching import Batch
from plone.app.content.browser.tableview import Table, TableKSSView
from plone.memoize import instance
from slc.treecategories.widgets.widgets import getInlineTreeView
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter #@UnresolvedImport
from zope.i18n import translate
import urllib

SUPPORTED_PORTAL_TYPES = ('Image', 'File', 'Link')

class CustomizedTable(Table):
    render = ViewPageTemplateFile("templates/table.pt")
    batching = ViewPageTemplateFile('templates/batching.pt')

class CustomizedFolderContentsTable(FolderContentsTable):

    def __init__(self, context, request, contentFilter=None):
        if contentFilter == None:
            contentFilter = {}
        
        contentFilter.update(request.form)
        super(CustomizedFolderContentsTable, self).__init__(context, request, contentFilter)

        url = context.absolute_url()
        
        filters = []
        for filter_key in ('Subject', 'SearchableText'): 
            if request.form.has_key(filter_key):
                filters.append("%s=%s" % (filter_key, request.form[filter_key]))
        filter_url = "&".join(filters)

        view_url = '?'.join((url + '/@@bulk_tagger', filter_url))
        self.table = CustomizedTable(request, url, view_url, self.items,
                                     show_sort_column=self.show_sort_column,
                                     buttons=self.buttons)

    @property
    @instance.memoize
    def items(self):
        """
        """
        context = aq_inner(self.context)
        plone_utils = getToolByName(context, 'plone_utils')
        plone_view = getMultiAdapter((context, self.request), name=u'plone')
        portal_workflow = getToolByName(context, 'portal_workflow')
        portal_properties = getToolByName(context, 'portal_properties')
        portal_types = getToolByName(context, 'portal_types')
        site_properties = portal_properties.site_properties

        use_view_action = site_properties.getProperty('typesUseViewActionInListings', ())
        browser_default = context.browserDefault()

        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = context.getFolderContents

        results = []
        for i, obj in enumerate(contentsMethod(self.contentFilter)):
            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = obj.getURL()
            path = obj.getPath or "/".join(obj.getPhysicalPath())
            icon = plone_view.getIcon(obj);

            type_class = 'contenttype-' + plone_utils.normalizeString(
                obj.portal_type)

            review_state = obj.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = obj.getURL(relative=True)

            type_title_msgid = portal_types[obj.portal_type].Title()
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(obj.Description))

            modified = plone_view.toLocalizedTime(
                obj.ModificationDate, long_format=1)

            obj_type = obj.Type
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                obj.id == browser_default[1][0])
            
            subcategory = multilingualthesaurus = nace = ""
            
            if obj.portal_type not in SUPPORTED_PORTAL_TYPES:
                continue

            if not hasattr(self, 'subcategory_field'):
                self.subcategory_field = obj.getObject().Schema()['subcategory']
            subcategory = getInlineTreeView(self.context, obj, self.request, self.subcategory_field).render
            if not hasattr(self, 'mt_field'):
                self.mt_field = obj.getObject().Schema()['multilingual_thesaurus']
            multilingualthesaurus = getInlineTreeView(self.context, obj, self.request, self.mt_field).render
            if not hasattr(self, 'nace_field'):
                self.nace_field = obj.getObject().Schema()['nace']
            nace = getInlineTreeView(self.context, obj, self.request, self.nace_field).render

            results.append(dict(
                url=url,
                url_href_title=url_href_title,
                id=obj.getId,
                quoted_id=urllib.quote_plus(obj.getId),
                path=path,
                title_or_id=obj.pretty_title_or_id(),
                obj_type=obj_type,
                size=obj.getObjSize,
                modified=modified,
                icon=icon.html_tag(),
                type_class=type_class,
                wf_state=review_state,
                state_title=portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class=state_class,
                is_browser_default=is_browser_default,
                folderish=obj.is_folderish,
                relative_url=relative_url,
                view_url=view_url,
                table_row_class=table_row_class,
                is_expired=context.isExpired(obj),
                subcategory=subcategory,
                multilingualthesaurus=multilingualthesaurus,
                nace=nace
            ))
        return results

class CustomizedFolderContentsView(FolderContentsView):
    enabled = True
    def contents_table(self):
        table = CustomizedFolderContentsTable(aq_inner(self.context), self.request)
        return table.render()

class FolderContentsKSSView(TableKSSView):
    table = CustomizedFolderContentsTable
