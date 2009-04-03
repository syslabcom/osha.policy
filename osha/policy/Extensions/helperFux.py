from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from Products.OSHATranslations import OSHAMessageFactory as _
from plone.app.portlets.portlets import navigation, news, classic, events, search
from StringIO import StringIO
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from zope.component import getMultiAdapter, getUtility
import Acquisition


def helper(self, key):
    print "\nhelper"
    
    path = '/'.join(self.getPhysicalPath())
    
    portal = self.portal_url.getPortalObject()
    portal_path = self.portal_url.getPortalPath()
    langs = portal.portal_languages.getSupportedLanguages()
    
    right = assignment_mapping_from_key(self, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
    print right.keys()
    from plone.portlet.collection import collection as collection_portlet
    
    #key = 'organisation'
    topic_path = "%s/directory/%s/Publication" %(portal_path, key)
    right[u'sep_publications'] = collection_portlet.Assignment(header=_(u"legend_publications"), 
                                   target_collection=topic_path, 
                                   limit=5)
    
    return "ok"


def LanguageSetter(self, lang=''):
    print "\n LanguageSetter"
    
    objs = self.objectValues()
    for obj in objs:
        obj._md['language'] = lang
        obj.reindexObject()

    return "ok"

def setNewsEvents(self):

    portal = self.portal_url.getPortalObject()
    portal_path = self.portal_url.getPortalPath()
    langs = portal.portal_languages.getSupportedLanguages()
    out = StringIO()

    folders = [ 
                'good_practice', 
                'good_practice/topics', 'good_practice/topics/accident_prevention', 
                'good_practice/topics/msd', 'good_practice/topics/whp', 'good_practice/topics/stress', 
                'good_practice/topics/dangerous_substances', 'good_practice/topics/noise',
                'good_practice/sector', 'good_practice/sector/construction', 'good_practice/sector/agriculture',
                'good_practice/sector/eductation', 'good_practice/sector/fisheries', 
                'good_practice/sector/healthcare','good_practice/sector/horeca', 'good_practice/sector/road_transport',  
                'good_practice/priority_groups', 'good_practice/priority_groups/disability', 
                'good_practice/priority_groups/gender', 'good_practice/priority_groups/young_people',
#                'about', 'about/organisation', 'about/jobs', 'about/partners', 'about/director_corner', 'about/calls', 'about/contact_us',
#                'topics', 'topics/prevent', 'topics/business', 'topics/change', 'topics/ds', 'topics/osheducation',
#                'topics/msds', 'topics/noise', 'topics/stress', 'topics/whp',
#                'sector', 'sector/agriculture', 'sector/construction', 'sector/education', 'sector/fisheries', 'sector/healthcare',
#                'sector/horeca',
#                'priority_groups', 'priority_groups/ageingworkers', 'priority_groups/migrant_workers', 'priority_groups/disability',
#                'priority_groups/sme', 'priority_groups/gender', 'priority_groups/young_people',
#                'campaigns', 
#                'press', 
#                'publications', 
#                'legislation', 
#                'statistics'
              ]

    for fname in folders:
        f_path = "%s/%s/%s" %(portal_path, 'en', fname)
        f = self.restrictedTraverse(f_path, None)
        if f is None: 
            #import pdb; pdb.set_trace()
            out.write('Not found: %s \n' % f_path)
            continue
        for lang in langs:
            f_trans = f.getTranslation(lang)
            if not f_trans: 
                out.write('No trnslation for %s in %s \n' %(f_path, lang))
                continue
            indexpage = f_trans.getDefaultPage()
            #out.write('\nindexpage: ' + str([indexpage]))
            if not indexpage:
                out.write('\tNo default page for %s in %s\n' %(f_path, lang))
                continue
            d = getattr(f_trans, indexpage, None)
            if not d:
                out.write('\tNo default page for %s in %s\n' %(f_path, lang))
                continue
            
            path = '/'.join(d.getPhysicalPath())
            #out.write('path:' + path + ' d: '+ str(d) + '\n'); continue
            if d.portal_type=='LinguaLink': continue
            below =  assignment_mapping_from_key(d, 'osha.belowcontent.portlets', CONTEXT_CATEGORY, path)

            for x in list(below.keys()):
                del below[x]

            below['news'] = news.Assignment()
            below['events'] = events.Assignment()

    return out.getvalue()

def copyPortletsFromParent(self, doleft=False, doright=False):
        out = StringIO()
        parent= Acquisition.aq_parent(Acquisition.aq_inner(self))
        ppath = "/".join(parent.getPhysicalPath())
        pleft = assignment_mapping_from_key(parent, 'plone.leftcolumn', CONTEXT_CATEGORY, ppath)
        pright = assignment_mapping_from_key(parent, 'plone.rightcolumn', CONTEXT_CATEGORY, ppath)

        ob = Acquisition.aq_inner(self)
        out.write("Copying portlets from parent %s to here %s\n" %(parent.absolute_url(), ob.absolute_url()))
        path = "/".join(ob.getPhysicalPath())
        left = assignment_mapping_from_key(ob, 'plone.leftcolumn', CONTEXT_CATEGORY, path)
        right = assignment_mapping_from_key(ob, 'plone.rightcolumn', CONTEXT_CATEGORY, path)

        if doleft:
            out.write('Copied left portlets\n')
            for x in list(left.keys()):
                del left[x]
            for x in list(pleft.keys()):
                left[x] = pleft[x]
        else:
            out.write('Left portlets NOT copied\n')

        if doright:
            out.write('Copied right portlets\n')
            for x in list(right.keys()):
                del right[x]
            for x in list(pright.keys()):
                right[x] = pright[x]
        else:
            out.write('Right portlets NOT copied\n')

        return out.getvalue()

def fixDEPortlets(self):
  path = '/osha/portal/fop/germany'
  cat = self.portal_catalog
  portletManager = getUtility(IPortletManager, name='plone.rightcolumn')
  res = cat(path=path,Language='all',portal_type="RichDocument")
  
  for r in res:
    try:
      ob = r.getObject()
    except:
      print "Err in getObject, skipping"
      pass
    path = "/".join(ob.getPhysicalPath())
    right = assignment_mapping_from_key(ob, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
    assignable = getMultiAdapter((ob, portletManager,), ILocalPortletAssignmentManager)
    portlets = [x for x in list(right.keys())]
    if portlets!=['portlet_themenbezogen', 'portlet_oshsearch'] and portlets!=[]:
      print "abweichende portlets auf %s: %s" %(r.getURL(), portlets)
      pass
    for k in portlets:
      del right[k]
    assignable.setBlacklistStatus(CONTEXT_CATEGORY, False)
  
    

  return len(res)
