from plone.app.portlets.utils import assignment_mapping_from_key
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from Products.OSHATranslations import OSHAMessageFactory as _
from plone.app.portlets.portlets import navigation, news, classic, events, search
from StringIO import StringIO
from plone.portlets.constants import CONTEXT_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY
from plone.portlets.interfaces import IPortletManager, ILocalPortletAssignmentManager
from zope.component import getMultiAdapter, getUtility
import Acquisition
from Products.CMFCore.utils import getToolByName
import transaction
from DateTime import DateTime
import time

types_to_dest = dict(
    OSH_Link='data/links',
    Provider='data/provider',
    RALink='data/risk-assessment-links',
    CaseStudy='data/case-studies'
  )

def reindexDBcontent(self, ptype='OSH_Link', thresh=200, start_from=0):
  pu = getToolByName(self, 'portal_url')
  portal = pu.getPortalObject()
  start = DateTime()

  parent = portal.restrictedTraverse(types_to_dest.get(ptype, None), None)
  if not parent:
    return "relevant data folder not found"
  print "got folder:", parent.absolute_url()
  cnt = 0
  fh = open('/tmp/reindex.log','a')
  fh.write('Start reindex of %s at %s\n\n' %(ptype, start))
  fh.write('Iterating over contents of %s\n' % parent.absolute_url())
  fh.write('Starting at %d\n' % start_from)
  objs = list()
  for id in parent.objectIds()[start_from:]:
    try:
      ob = getattr(parent, id, None)
      if ob:
        objs.append(ob)
    except:
      fh.write('Could not get %s\n' %id)
#  for ob in parent.objectValues()[start_from:]:
  for ob in objs:
    try:
      ob.reindexObject()
    except:
      print "ERROR: %s" % ob.absolute_url()
      fh.write("ERROR: %s\n" % ob.absolute_url())
    cnt += 1
    if cnt % thresh == 0:
      try:
        transaction.commit()
        print "COMMIT after %d\n" % cnt
        fh.write("COMMIT after %d\n" % cnt)
      except:
        print "ERROR, could not commit after %d\n" % cnt
        fh.write("ERROR, could not commit after %d\n" % cnt)
        raise

      time.sleep(1)

  delta = (DateTime() - start) * 3600 * 24
  fh.write('\nFinished after %d seconds\n' % delta)
  fh.write('Processed %d items\n' % cnt)
  fh.close()

  return "finished after %d seconds" % delta



def exchangeSEPPortlets(self, key):
    portlet_name=u'sep_publications'
    
    path = '/'.join(self.getPhysicalPath())
    
    portal = self.portal_url.getPortalObject()
    portal_path = self.portal_url.getPortalPath()
    langs = portal.portal_languages.getSupportedLanguages()
    
    right = assignment_mapping_from_key(self, 'plone.rightcolumn', CONTEXT_CATEGORY, path)
    print right.keys()
    from osha.theme.portlets import oshcollection as collection_portlet
       
    if right.has_key(portlet_name):
        topic_path = right.get(portlet_name).target_collection
        del right[portlet_name]
    else:
        topic_path = "%s/directory/%s/Publication" %(portal_path, key)
    right[portlet_name] = collection_portlet.Assignment(header=_(u"legend_publications"), 
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


def redoEROCategorisation(self):
    cat = self.portal_catalog
    path = "/osha/portal/en/riskobservatory/"
    # first pass
    print "first pass\n"
    objs = set()
    topics = cat.uniqueValuesFor('ero_topic')
    replacer = dict(hearingloss='hearing_loss', paceofwork='pace_of_work', 
        workingtime='working_time', noiseexposure='noise_exposure')
    for topic in topics:
        res = cat(ero_topic=topic, portal_type="RichDocument", path=path)
        print "%d results for %s" %(len(res), topic)
        for r in res:
            o = r.getObject()
            if not o:
                print "err, object is None"
                continue
            md = o.getOsha_metadata()
            newmd = set(md)
            topic = replacer.get(topic, topic)
            newmd.add('ero_topic::%s'%topic)
            newmd = tuple(newmd)
            #print "new md: ", newmd
            o.setOsha_metadata(newmd)
            objs.add(o)
    
    print "second pass"
    target_groups = cat.uniqueValuesFor('ero_target_group')
    for target_group in target_groups:
        res = cat(ero_target_group=target_group, portal_type="RichDocument", path=path)
        print "%d results for %s" %(len(res), target_group)
        for r in res:
            o = r.getObject()
            if not o:
                print "err, object is None"
                continue
            md = o.getOsha_metadata()
            newmd = set(md)
            if target_group == "employmentstatus":
                target_group = "employment_status"
            newmd.add('ero_target_group::%s'%target_group)
            newmd = tuple(newmd)
            #print "new md: ", newmd
            o.setOsha_metadata(newmd)
            objs.add(o)
    
    print "reindxing %d objects" %len(objs)
    for o in tuple(objs):
        o.reindexObject()
    
    return "fine"


def hasVersionInfo(obj, tool=None):
    if not tool:
        tool = getToolByName(obj, 'portal_archivist')
    history = tool.queryHistory(obj, default=None)
    return bool(history and len(history))


def updateLC(self):
    lc = getToolByName(self, 'portal_linkchecker')
    print "_updateWSRegistrations"
    lc.database._updateWSRegistrations()
    return "updated"
