from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from urlparse import urljoin
from osha.policy.browser.interfaces import ILinkcheckerOSHA


class CSVExportView(BrowserView):
    
    def __call__(self, link_state='red', path_filter='', multilingual_thesaurus=[], subcategory=[]):
        """ export the database in csv format """
        lcosha = getMultiAdapter((self.context, self.request), name='lc_osha_view')
        links = lcosha.LinksInState(state=link_state, 
                                    b_start=0, 
                                    b_size=-1, 
                                    path_filter=path_filter, 
                                    multilingual_thesaurus=multilingual_thesaurus, 
                                    subcategory=subcategory
                                    )
        self.request.RESPONSE.setHeader('Content-Type', 'text/csv')
        self.request.RESPONSE.setHeader('Content-Disposition', 'attachment;filename=linkchecker_state_%s.csv' % link_state)
        wr = self.request.RESPONSE.write                                  
        wr("Document,Brokenlink,Reason,Lastcheck\n")                                    
        links = [x for x in links]
        for link in links:
            if link is None or len(link.keys())==0:
                continue
            wr(",".join([link['document'].getPath(), link['url'],link['reason'],str(link['lastcheck'])]) +'\n') 
            
class LinkcheckerOSHA(BrowserView):
    implements(ILinkcheckerOSHA)

    def LinksInState(self, state, b_start=0, b_size=15, path_filter='', multilingual_thesaurus=[], subcategory=[]):
        """Returns a list of links in the given state."""
        
        multilingual_thesaurus = [ x for x in multilingual_thesaurus if x!= '']
        if not len(multilingual_thesaurus): multilingual_thesaurus=''
        subcategory = [ x for x in subcategory if x != '']
        if not len(subcategory): subcategory = ''

        # If one or more filter parameters were passed in, use the filter based method
        if path_filter or len(multilingual_thesaurus) or len(subcategory):
            portal_url = getToolByName(self.context, 'portal_url')
            if path_filter:
                portal_path = '/'.join(portal_url.getPortalObject().getPhysicalPath() + ('',))
                if path_filter[0]=='/': path_filter = path_filter[1:]
                abspath = urljoin(portal_path, path_filter)
            else:
                abspath = ''
            for link, doc, member in self._document_iterator_path(state, b_start, b_size, abspath, multilingual_thesaurus, subcategory):
                if link is None: 
                    yield {}
                    continue
                item = {}
                item["url"] = link.url
                item["reason"] = link.reason
                item["lastcheck"] = link.lastcheck
                item["id"] = link.getId
                item["link"] = link.link
                item["document"] = doc
                item["object"] = link.object
    
                #if member is None:
                item["owner_mail"] = ""
                item["owner"] = doc.Creator
                #else:
                #    item["owner_mail"] = member.getProperty("email")
                #    item["owner"] = member.getProperty("fullname", doc.Creator)
    
                yield item

        # Else, use the regular methor for retrieving link
        else:
            for link, doc, member in self._document_iterator(state, b_start, b_size):
                if link is None: 
                    yield {}
                    continue
                item = {}
                item["url"] = link.url
                item["reason"] = link.reason
                item["lastcheck"] = link.lastcheck
                item["id"] = link.getId
                item["link"] = link.link
                item["document"] = doc
                item["object"] = link.object
    
                #if member is None:
                item["owner_mail"] = ""
                item["owner"] = doc.Creator
                #else:
                #    item["owner_mail"] = member.getProperty("email")
                #    item["owner"] = member.getProperty("fullname", doc.Creator)
    
                yield item



    def _document_iterator(self, state, b_start, b_size):

        member_cache = {}

        lc = getToolByName(self.context, 'portal_linkchecker')
        catalog = getToolByName(self.context, 'portal_catalog')
        pms = getToolByName(self.context, 'portal_membership')

        _marker = object()

        links = lc.database.queryLinks(state=[state], sort_on="url")
        #print "len links:", len(links)
        #print "b_start", b_start

        for dummy in range(b_start):
            yield None, None, None
            
        counter =0
        valid_cnt = 0
        if b_size==-1:
            b_size=len(links)
#        for link in links[b_start:b_start+b_size]:
        while (valid_cnt < b_size):
            ind = b_start+counter
            if ind>=len(links): break
            link = links[ind]
            counter += 1
            doc_uid = link.object
            if not doc_uid:
                print "continue, no doc_uid"
                continue
            docs = catalog(UID=doc_uid, Language='all')
            if not len(docs):continue
            valid_cnt += 1
            for doc in docs:
                creator = doc.Creator
                member = member_cache.get(creator, _marker)
                #if member is _marker:
                #    member = pms.getMemberById(creator)
                #    member_cache[creator] = member
                yield link, doc, member

        invalids = counter-valid_cnt
        for dummy in range(len(links)-(b_start+b_size+invalids)):
            yield None, None, None



    def _document_iterator_orig(self, state):
        member_cache = {}
    
        lc = getToolByName(self.context, 'portal_linkchecker')
        catalog = getToolByName(self.context, 'portal_catalog')
        pms = getToolByName(self.context, 'portal_membership')

        _marker = object()

        links = lc.database.queryLinks(state=[state], sort_on="url")
        print "reports::_document_iterator, number of links in state %s: %d" %(state, len(links))
        for link in links:
            doc_uid = link.object
            if not doc_uid:
                print "continue, no doc_uid for ", [link]
                continue
            docs = catalog(UID=doc_uid, Language='all')
            if not len(docs):
                print "no docs for doc_uid ", doc_uid , " of link", [link]
            for doc in docs:
                creator = doc.Creator
                member = member_cache.get(creator, _marker)
                if member is _marker:
                    member = pms.getMemberById(creator)
                    member_cache[creator] = member
                yield link, doc, member



    def _document_iterator_path(self, state, b_start, b_size, path_filter, multilingual_thesaurus, subcategory):
        print "path_filter:", path_filter
        print "multilingual_thesaurus:", multilingual_thesaurus
        print "subcategory:", subcategory
        member_cache = {}

        lc = getToolByName(self.context, 'portal_linkchecker')
        catalog = getToolByName(self.context, 'portal_catalog')
        pms = getToolByName(self.context, 'portal_membership')

        _marker = object()

        links = lc.database.queryLinks(state=[state], sort_on="url")
        print "len links before", len(links)
        filtered_res = catalog( Language='all', path=path_filter, multilingual_thesaurus=multilingual_thesaurus, subcategory=subcategory)
        filtered_uids = [x.UID for x in filtered_res]
        links = [x for x in links if x.object in filtered_uids]
        print "len links after", len(links)


        for dummy in range(b_start):
            yield None, None, None

        counter =0
        valid_cnt = 0
        if b_size==-1:
            b_size=len(links)
#        for link in links[b_start:b_start+b_size]:
        while (valid_cnt < b_size):
            ind = b_start+counter
            if ind>= len(links): break
            link = links[ind]
            counter +=1
            doc_uid = link.object
            if not doc_uid:
                continue
            docs = catalog(UID=doc_uid, Language='all')
            if len(docs)==0: continue
            valid_cnt += 1
            for doc in docs:
                creator = doc.Creator
                member = member_cache.get(creator, _marker)
                yield link, doc, member

        invalids = counter-valid_cnt
        for dummy in range(len(links)-(b_start+b_size+invalids)):
            yield None, None, None
