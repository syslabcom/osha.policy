from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from logging import getLogger



def ws_add_news(self,id,title,description,text,effective,image):

    portal = getToolByName(self, 'portal_url').getPortalObject()
    pwt = portal.portal_workflow

    log = getLogger('/en/campaigns/hw2010/events/ws_add_news')

    targetfolder = portal.en.campaigns.hw2010.news
###    targetfolder.invokeFactory(id=id, type_name=u"News Item")
    targetfolder.manage_addProduct['ATContentTypes'].addATNewsItem(id)


    ob = getattr(targetfolder, id, None)
    if ob is None:
        return "Error, object not found"


    ob.setTitle(title)
    # all news items are language neutral I assume
    ob.setLanguage('')
    ob.setDescription(description)
    ob.setText(text)
    ob.setEffectiveDate(DateTime(effective))
    ob.setImage(image.data)


    # set the subject
    ob.setSubject('maintenance')

    log.info('Created new News Item at %s' %ob.absolute_url())


    # publish
    try:
        pwt.doActionFor(ob, 'publish')
    except:
        log.warn('Publishing the News Item was not possible!')

    ob.reindexObject()

    return 0

