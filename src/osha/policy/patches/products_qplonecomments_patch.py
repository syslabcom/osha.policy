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


mod_names = ['Products', 'qPloneComments', 'interfaces']
for i in range(len(mod_names)):
    full_mod_name = ".".join(mod_names[:i+1])

    if full_mod_name not in sys.modules.keys():
        m = imp.new_module(full_mod_name)
        parent_mod_name = ".".join(mod_names[:i])
        setattr(sys.modules[parent_mod_name], mod_names[i], m)
        sys.modules[full_mod_name] = m
m.IPloneCommentsLayer = Interface
