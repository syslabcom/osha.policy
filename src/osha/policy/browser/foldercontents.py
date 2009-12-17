import urllib
import logging

from Acquisition import aq_inner

from zope.app.pagetemplate import ViewPageTemplateFile
from zope.component import getMultiAdapter #@UnresolvedImport
from zope.i18n import translate

from plone.memoize import instance

from plone.app.content.batching import Batch
from plone.app.content.browser.foldercontents import FolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.tableview import Table, TableKSSView

from Products.ATContentTypes.interface import IATTopic
from Products.Archetypes.interfaces import ISchema
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

log = logging.getLogger("osha.policy/foldercontents.py")
try:
    from slc.treecategories.widgets.widgets import getInlineTreeView
except ImportError:
    log.warn("slc.treecategories not found")
    getInlineTreeView = None


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
        self.table.portal = getToolByName(context, 'portal_url').getPortalObject()

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
        for i, brain in enumerate(contentsMethod(self.contentFilter)):
            # don't bother if the object doesn't support bulk-tagging
            if brain.portal_type not in SUPPORTED_PORTAL_TYPES:
                continue

            if (i + 1) % 2 == 0:
                table_row_class = "draggable even"
            else:
                table_row_class = "draggable odd"

            url = brain.getURL()
            path = brain.getPath() or "/".join(brain.getPhysicalPath())
            icon = plone_view.getIcon(brain);

            type_class = 'contenttype-' + plone_utils.normalizeString(
                brain.portal_type)

            review_state = brain.review_state
            state_class = 'state-' + plone_utils.normalizeString(review_state)
            relative_url = brain.getURL(relative=True)

            type_title_msgid = portal_types[brain.portal_type].Title()
            url_href_title = u'%s: %s' % (translate(type_title_msgid,
                                                    context=self.request),
                                          safe_unicode(brain.Description))

            modified = plone_view.toLocalizedTime(
                brain.ModificationDate, long_format=1)

            obj_type = brain.Type
            obj = brain.getObject()
            if obj_type in use_view_action:
                view_url = url + '/view'
            elif obj.is_folderish:
                view_url = url + "/folder_contents"
            else:
                view_url = url

            is_browser_default = len(browser_default[1]) == 1 and (
                brain.id == browser_default[1][0])

            subcategory = multilingualthesaurus = nace = ""

            is_canonical = obj.isCanonical()
            if not hasattr(self, 'subcategory_field'):
                self.subcategory_field = obj.getField('subcategory')
            if getInlineTreeView is not None:
                subcategory_pt = getInlineTreeView(self.context, brain, self.request, self.subcategory_field)
                subcategory_mode = (is_canonical or not self.subcategory_field.languageIndependent) and 'edit' or 'view'
                subcategory = subcategory_pt.render.macros.get(subcategory_mode)
                if not hasattr(self, 'mt_field'):
                    self.mt_field = obj.getField('multilingual_thesaurus')
                multilingualthesaurus_pt = getInlineTreeView(self.context, brain, self.request, self.mt_field)
                multilingualthesaurus_mode = (is_canonical or not self.mt_field.languageIndependent) and 'edit' or 'view'
                multilingualthesaurus = multilingualthesaurus_pt.render.macros.get(multilingualthesaurus_mode)
                if not hasattr(self, 'nace_field'):
                    self.nace_field = obj.getField('nace')
                nace_pt = getInlineTreeView(self.context, brain, self.request, self.nace_field)
                nace_mode = (is_canonical or not self.nace_field.languageIndependent) and 'edit' or 'view'
                nace = nace_pt.render.macros.get(nace_mode)
            else:
                error_msg = "slc.treecategories not available"
                subcategory = multilingualthesaurus = nace = error_msg
                subcategory_mode = multilingualthesaurus_mode = nace_mode = \
                                   "view"

            results.append(dict(
                url=url,
                url_href_title=url_href_title,
                id=brain.getId,
                quoted_id=urllib.quote_plus(brain.getId),
                path=path,
                title_or_id=brain.pretty_title_or_id(),
                obj_type=obj_type,
                size=brain.getObjSize,
                modified=modified,
                icon=icon.html_tag(),
                type_class=type_class,
                wf_state=review_state,
                state_title=portal_workflow.getTitleForStateOnType(review_state,
                                                           obj_type),
                state_class=state_class,
                is_browser_default=is_browser_default,
                folderish=brain.is_folderish,
                relative_url=relative_url,
                view_url=view_url,
                table_row_class=table_row_class,
                is_expired=context.isExpired(brain),
                subcategory=subcategory,
                multilingualthesaurus=multilingualthesaurus,
                nace=nace,
                subcategory_mode=subcategory_mode,
                multilingualthesaurus_mode=multilingualthesaurus_mode,
                nace_mode=nace_mode,
                context=obj,
            ))
        return results

class CustomizedFolderContentsView(FolderContentsView):
    enabled = True
    def contents_table(self):
        table = CustomizedFolderContentsTable(aq_inner(self.context), self.request)
        return table.render()

class FolderContentsKSSView(TableKSSView):
    table = CustomizedFolderContentsTable
