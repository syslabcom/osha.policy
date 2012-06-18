# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName


def resetWysiwyg(self):
    pm = getToolByName(self, 'portal_membership')
    f = pm.getMembersFolder()
    changed = skipped = 0
    for id in f.objectIds('ATFolder'):
        member = pm.getMemberById(id)
        if member:
            member.setMemberProperties({'wysiwyg_editor': 'CKeditor'})
	    try:
                name = member.getUserId()
            except:
                name = member.getId()
            print "Set editor for member %s" % name
            changed += 1
        else:
            print "No member found for %s" % id
            skipped += 1

    return "Changed %d members and skipped %d" % (changed, skipped)

