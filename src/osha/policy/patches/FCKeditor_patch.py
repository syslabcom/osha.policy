from Products.CMFCore.utils import getToolByName
from Products.FCKeditor import utils as FCKutils

# reason for this patch:
# ATBlob's portal_type (as File replacement) is NOT File, but Blob. This needs to be changed to File
# in listTypesForInterface, because the type is also registered as File
# But we CANNOT pass portalTypes=True, because that would exclude Image (ATImage)

def listTypesForInterface(portal, interface):
    """
    List of portal types that have File interface
    @param portal: plone site
    @param interface: Zope 2 inteface
    @return: [{'portal_type': xx, 'type_ui_info': UI type info}, ...]
    """

    archetype_tool = getToolByName(portal, 'archetype_tool')
    portal_types = getToolByName(portal, 'portal_types')
    utranslate = portal.utranslate

    # all_types = [{'name': xx, 'package': xx, 'portal_type': xx, 'module': xx,
    #               'meta_type': xx, 'klass': xx, ...
    all_types = archetype_tool.listRegisteredTypes(inProject=True, portalTypes=False)
    # Keep the ones that are file like
    all_types = [tipe['portal_type'] for tipe in all_types
                 if interface.isImplementedByInstancesOf(tipe['klass'])]

    # XXX fix for Blob, which is actually a File:
    if 'Blob' in all_types:
        all_types[all_types.index('Blob')] = 'File'

    # Keep allowed ones
    # removed some types can be allowed in some context
    # all_types = [tipe for tipe in all_types
    #             if getattr(portal_types, tipe).globalAllow()]
    return [FCKutils.infoDictForType(tipe, portal_types, utranslate) for tipe in all_types]


FCKutils.listTypesForInterface = listTypesForInterface
