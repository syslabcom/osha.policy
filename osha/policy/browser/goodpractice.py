from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

class GoodPracticeView(BrowserView):
    """View for displaying the dynamic good practice overview page at /good_practice
    """
    template = ViewPageTemplateFile('goodpractice.pt')
    gpawards = ''
    intro = ''
    
    def __call__(self):
        self.request.set('disable_border', True)
        

        intro = getattr(self.context, 'introduction_html', None)
        if intro is None:
            self.intro = ''
        else:
            self.intro = intro.CookedBody()
        
        gpaward = getattr(self.context, 'good_practice_awards_html', None)
        if gpaward is None:
            self.gpaward = ''
        else:
            self.gpaward = gpaward.CookedBody()

        return self.template() 

    def getAreaLinks(self, area=''):
        """ return the SEPS under topics """
        path = "/".join(self.context.getPhysicalPath())+'/' +area
        pc = getToolByName(self.context, 'portal_catalog')
        res = pc(path={'query': path, 'depth': 1})
        return res
        
        
    def getLatestLink(self):
        """ Return latest link """
        pc = getToolByName(self.context, 'portal_catalog')
        res = pc(portal_type='OSH_Link', review_state='published', sort_on='effective', sort_order='reverse', limit=1) 
        if len(res)==0:
            latestLink = None
        else:              
            latestLink = res[0].getObject()
        

        return latestLink