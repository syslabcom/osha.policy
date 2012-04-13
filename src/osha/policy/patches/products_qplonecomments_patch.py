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
    "p4a.calendar.interfaces.ICalendarEnhanced",
    "Products.qPloneComments.interfaces.IPloneCommentsLayer",
    "slc.calendarfetcher.browser.interfaces.ICalendarFetcherLayer",
    "p4a.video.interfaces.IVideoEnhanced",
    "Products.CMFCore.interfaces.Contentish.Contentish",
    "webdav.WriteLockInterface.WriteLockInterface"
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
            setattr(sys.modules[parent_mod_name], module_list[i], m)
            sys.modules[full_mod_name] = m
    setattr(m, interface, Interface)
