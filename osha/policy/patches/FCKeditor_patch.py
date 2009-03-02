from Products.CMFCore.utils import getToolByName
from Products.FCKeditor import utils as FCKutils

# The original method is not passing the param portalTypes=True to the
# archetype_tool. This leads to problems with ATBlob. Its portal_type is
# File, but w/o the param, the tool returns Blob.

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
    all_types = archetype_tool.listRegisteredTypes(inProject=True, portalTypes=True)
    # Keep the ones that are file like
    all_types = [tipe['portal_type'] for tipe in all_types
                 if interface.isImplementedByInstancesOf(tipe['klass'])]
    # Keep allowed ones
    # removed some types can be allowed in some context
    # all_types = [tipe for tipe in all_types
    #             if getattr(portal_types, tipe).globalAllow()]
    return [FCKutils.infoDictForType(tipe, portal_types, utranslate) for tipe in all_types]


FCKutils.listTypesForInterface = listTypesForInterface

