from interfaces import IDateTimeUtils
from Products.CMFCore.utils import getToolByName

from zope.interface import implements
from Products.CMFPlone import utils
from DateTime import DateTime
from Products.Five import BrowserView

class DateTimeUtils(BrowserView):
    implements(IDateTimeUtils)

    def toPortalTime(self, time=None, long_format=None):
        context = utils.context(self)
        localized_time=None

        portal_properties = getToolByName(context, 'portal_properties')
        properties = portal_properties.site_properties
        if long_format:
            format = properties.get('localLongTimeFormat', '%d.%m.%Y %H:%M')
        else:
            format = properties.get('localTimeFormat', '%d.%m.%Y')

        err = ''
        if not time:
            time=DateTime().pCommon()

        mintime = DateTime('1974/01/01')
        maxtime = DateTime('2037/12/30')
        try:
            giventime = DateTime(str(time))
        except:
            giventime = time
        
        if giventime > maxtime:
            giventime = maxtime
        if giventime < mintime:
            giventime = mintime

        try:
            localized_time=giventime.strftime(format)
        except IndexError:
            localized_time = str(giventime).replace('/','-')
        except:
            localized_time = str(giventime).replace('/','-')
        
        return localized_time
