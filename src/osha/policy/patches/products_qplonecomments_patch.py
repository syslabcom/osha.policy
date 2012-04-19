"""
Provides a dummy
Products.qPloneCommnets.interfaces.IPloneCommentsLayer
to work around a pickling error

Based on
http://stackoverflow.com/questions/5423239/picklingerror-while-installing-add-on
http://davisagli.com/blog/the-making-of-zodb.ws
"""
import imp, sys

from zope.interface import Interface


dummy_modules = [
    "Products.CMFCore.interfaces.Contentish.Contentish",
    "Products.CMFCore.interfaces.Dynamic.DynamicType",
    "Products.qPloneComments.interfaces.IPloneCommentsLayer",
    "p4a.calendar.interfaces.ICalendarEnhanced",
    "p4a.calendar.interfaces.ICalendarSupport",
    "p4a.video.interfaces.IVideoEnhanced",
    "slc.calendarfetcher.browser.interfaces.ICalendarFetcherLayer",
    "slc.clicksearch.interfaces.IClickSearchConfiguration",
    "webdav.WriteLockInterface.WriteLockInterface",
    'p4a.plonevideoembed.interfaces.IVideoLinkEnhanced',
    'wildcard.fixpersistentutilities.classfactory.IFakeInterface'
    ]

for module in dummy_modules:
    dotted_name = module.split(".")
    module_list = dotted_name[:-1]
    interface = dotted_name[-1:][0]

    for i in range(len(module_list)):
        full_mod_name = ".".join(module_list[:i+1])

        if full_mod_name not in sys.modules.keys():
            m = imp.new_module(full_mod_name)
            parent_mod_name = ".".join(module_list[:i])
            sys.modules[full_mod_name] = m
            if parent_mod_name != "":
                setattr(sys.modules[parent_mod_name], module_list[i], m)

    setattr(m, interface, Interface)
