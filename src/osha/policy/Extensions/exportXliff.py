from slc.xliff.interfaces import IXLIFF
from slc.xliff.xliff import XLIFFExporter

def export(self):
    """ export the current context and all subobjects as xliff """
    xliff_exporter = XLIFFExporter(self)
    xliff_exporter.single_file = True
    xliff_exporter.html_compatibility = True
    xliff_exporter.source_language = self.Language()
    xliff_exporter.recursive = True
    self.REQUEST.response.write(xliff_exporter.export())
