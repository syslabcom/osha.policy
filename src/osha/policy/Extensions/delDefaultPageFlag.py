import Acquisition
def delDefaultPageFlag(self):
    if hasattr(Acquisition.aq_base(self), '_lp_defualt_page'):
        delattr(self, '_lp_default_page')
        return "deleted"
    return "no flag present"
