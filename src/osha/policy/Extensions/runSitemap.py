import ZPublisher, transaction
from gzip import GzipFile
from cStringIO import StringIO

print "Starting to fetch sitemap"
basepath = '/osha/portal'
ZPublisher.Zope('%s/sitemap.xml.gz' % basepath, s=1)
portal = app.osha.portal

def fixme(sitemap):
    data = str(sitemap)
    infile = StringIO(data)
    gzip = GzipFile(sitemap.getId(), 'r', 9, infile)
    data = gzip.read()

    data = data.replace('http://127.0.0.1/Zope%s' %basepath, 'http://osha.europa.eu')

    outfile = StringIO()
    gzip = GzipFile(sitemap.getId(), 'w', 9, outfile)
    gzip.write(data)
    gzip.close()
    data = outfile.getvalue()
    outfile.close()        
    sitemap.update_data(data)
    transaction.commit()

for i in portal.objectIds():
    if i.startswith('sitemap_'):
        fixme(getattr(portal, i))
print "Fetched"
