#!/usr/bin/env python
# Dependencies:
# pypdf:    easy_install pypdf

import elementtree
import logging
import optparse
import os
import pyPdf
import re
import subprocess

logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            )

def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)
    parser.add_option("-d", "--directory", dest="directory",
                    default='.',
                    help="Specify the directory in which the pdf files are "
                    "located"
                    )

    parser.add_option("-r", "--recursive", dest="recursive",
                    action="store_true",
                    default=False,
                    help="Indicate whether the given directory must be read " 
                    "recursively"
                    )
    options, args = parser.parse_args()

    read_directory(options.directory, options.recursive)

   
def read_directory(dirpath, recurse):
    """ Retrieve the pdf files from the directory with path dirpath
    """
    contents = os.listdir(dirpath)
    for file in contents:
        path = os.path.join(dirpath, file)
        if os.path.isdir(path) and recurse:
            read_directory(path, recurse)      
        elif path.rsplit('.')[-1] == 'pdf':
            command = 'pdftotext %s' % path.replace(' ', '\ ')
            os.system(command)

            txtpath = path.rsplit('.', 1)[0] + '.txt'
            txtfile = open(txtpath, "rb")

            lines = txtfile.readlines()
            title = lines[1]
            description = lines[3]

            command = 'rm %s' % txtpath.replace(' ', '\ ')
            os.system(command)

            pdffile = open(path, "rb")
            writer = pyPdf.PdfFileWriter()

        else:
            logging.info('Ignore file: %s' % path)


if __name__ == "__main__":
    main()


