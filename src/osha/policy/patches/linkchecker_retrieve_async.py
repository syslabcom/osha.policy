from gocept.linkchecker import retrievemanager, database
from gocept.linkchecker.link import Link
from gocept.linkchecker.url import URL
from osha.policy import handlers

retrievemanager.update_links = handlers.update_links
retrievemanager.remove_links = handlers.remove_links

database.LinkDatabase.updateManyStates = handlers.updateManyStates


def index(self):
    if self.getObject() is None:
        # only try this if REQUEST is present
        if getattr(self, 'REQUEST', None):
            self.getParentNode().manage_delObjects([self.id])
        return
    try:
        url = self.getURL()
    except ValueError:
        # Make sure the URL object exists when we index ourselves.
        url = URL(self.url())
        db = self.getLinkCheckerDatabase()
        if url.id not in db.objectIds():
            db._setObject(url.id, url)
        url = db[url.id]
    except AttributeError, err:
        # if the retriever is called a second time in async, the URL object
        # will aready exist. A getObject() on the brain in getURL will
        # fail, due to missing REQUEST
        # We therefore ignore this kind of error and assume the first run was
        # already successful
        if err.message == 'REQUEST':
            return
    path = '/'.join(self.getPhysicalPath())
    self.link_catalog.catalog_object(self, path)


Link.index = index
