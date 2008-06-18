from Products.Collage.browser.column import ExistingItemsView, COLLAGE_TYPES
from Products.CMFPlone import utils as cmfutils

def getItems(self):
    portal_type = self.request.get('portal_type', '').replace('+', ' ')
    SearchableText = self.request.get('SearchableText', '')
    items = self.catalog(portal_type=portal_type,
                         SearchableText=SearchableText,
                         sort_order='reverse',
                         sort_on='modified')
    # filter out collage content types
    items = [i for i in items if i.portal_type not in COLLAGE_TYPES]

    # limit count
    items = items[:self.request.get('count', 50)]

    # setup description cropping
    try:
        cropText = self.context.restrictedTraverse('@@plone').cropText
    except AttributeError:
        # BBB: Plone 2.5
        cropText = self.context.cropText

    props = cmfutils.getToolByName(self.context, 'portal_properties')
    site_properties = props.site_properties
    
    desc_length = getattr(site_properties, 'search_results_description_length', 25)
    desc_ellipsis = getattr(site_properties, 'ellipsis', '...')
    
    return [{'UID': obj.UID(),
             'icon' : result.getIcon,
             'title': result.Title,
             'description': cropText(result.Description, desc_length, desc_ellipsis),
             'type': result.Type,
             'portal_type':  self.normalizeString(result.portal_type),
             'modified': result.ModificationDate,
             'published': result.EffectiveDate or ''} for (result, obj) in
            map(lambda result: (result, result.getObject()), items)]

ExistingItemsView.getItems = getItems