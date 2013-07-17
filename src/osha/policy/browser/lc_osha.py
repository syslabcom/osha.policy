from App.config import getConfiguration
from DateTime import DateTime
from osha.policy.browser.interfaces import ILCMaintenanceView
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

import datetime
import sqlalchemy as sa
import zLOG


SQL_INS = (
    "INSERT INTO checkresults (state, document, brokenlink, reason, "
    "sitesection, lastcheck, subsite, portal_type) VALUES "
    "('%(state)s', '%(document)s', '%(brokenlink)s', '%(reason)s', "
    "'%(sitesection)s', '%(lastcheck)s', '%(subsite)s', '%(portal_type)s');"
)


def q(s):
    if s is None:
        return ''
    return s.replace('\\', '\\\\').\
        replace("'", "\\'").\
        replace('\r', '').\
        replace('\n', ' ').\
        replace('%', '%%').\
        replace('"', '\\"').\
        replace('\x00', '')


class LCMaintenanceView(BrowserView):
    """Contains the methods to report, retrieve and update the link checker."""
    implements(ILCMaintenanceView)

    def retrieve_and_notify(self):
        """Retrieve linkstates from zope to postgres and notify the lms on
        unregistered links. This should be called by a cronjob nightly.
        """
        start = DateTime()
        zLOG.LOG('osha Linkchecker', zLOG.INFO, "Starting retrieve_and_notify")
        self.notify_ws()

        states = ('orange', 'green', 'grey', 'red')
        for state in states:
            self.update_pg(link_state=state)

        stop = DateTime()
        delta = (stop - start) * 84600
        zLOG.LOG(
            'osha Linkchecker',
            zLOG.INFO,
            "Finished transmitting unregistered links to lms after "
            "%s seconds." % delta
        )
        return "update took %s seconds" % delta

    def notify_ws(self):
        """Notify the lms on unregistered links."""
        start = DateTime()
        zLOG.LOG(
            'osha Linkchecker',
            zLOG.INFO,
            "Starting to transmit unregistered links to lms"
        )
        db = self.context.portal_linkchecker.aq_inner.database
        db._updateWSRegistrations()
        stop = DateTime()
        delta = (stop - start) * 84600
        zLOG.LOG(
            'osha Linkchecker',
            zLOG.INFO,
            "Finished transmitting unregistered links to lms after "
            "%s seconds." % delta)

    def update_pg(self, link_state='red'):
        """Export the database to postgres."""
        portal_languages = getToolByName(self.context, 'portal_languages')
        self.langs = portal_languages.getSupportedLanguages()
        self.portal_path = self.context.portal_url.getPortalPath()
        configuration = getConfiguration()
        conf = configuration.product_config['osha.policy']
        pg_dsn = conf['osha.database']

        zLOG.LOG(
            'osha Linkchecker',
            zLOG.INFO,
            "Exporting link state %s to Postgres Database" % link_state)

        pgengine = sa.create_engine(pg_dsn, client_encoding='utf-8')
        pgconn = pgengine.connect()

        # clear the current table for all items with given state
        pgconn.execute(
            "delete from checkresults where state = '%s'" % link_state)

        sql = ""
        cnt = 0

        for item in self.links_in_state(state=link_state):
            doc = item['document']
            docpath = doc.getPath()
            subjects = doc.Subject or tuple()
            portal_type = doc.portal_type
            if subjects == tuple():
                subjects = ('',)

            # Careful: Here we count one record per section. If a link appears
            # in several sections it is counted several times. But as people
            # will look at the links from a section perspective we want the
            # broken links to appear everywhere. A total of all broken links
            # will not be correct if not done distinct by url and link!!
            for subject in subjects:
                toset = dict(
                    state=link_state,
                    document=docpath,
                    brokenlink=q(item["url"]),
                    reason=item["reason"],
                    sitesection=subject,
                    lastcheck=str(item["lastcheck"]) or '',
                    subsite=self.get_subsite(docpath),
                    portal_type=portal_type or ''
                )
                sql = sql + (SQL_INS % toset).decode('utf-8')
                cnt += 1
                if cnt % 1000 == 0:
                    with pgconn.begin():
                        pgconn.execute(sql)
                    sql = ''
                    ts = datetime.datetime.utcnow()
                    zLOG.LOG(
                        'osha Linkchecker',
                        zLOG.INFO,
                        "%s - Linkstate %s, wrote %s" % (ts, link_state, cnt))

        # execute the remaining insert statements (that were not done as part
        # of the 1k batch)
        if sql:
            with pgconn.begin():
                pgconn.execute(sql)

        zLOG.LOG('osha Linkchecker', zLOG.INFO, "Postgres Export Done")

    def get_subsite(self, path):
        path = path.replace(self.portal_path, '')
        elems = path.split('/')
        elems.reverse()
        # remove first elem, which is an empty string
        elems.pop()
        # remove language tree elem
        if elems[-1] in self.langs:
            elems.pop()
        if elems[-1] == 'fop':
            return elems[-2]
        if elems[-1] == 'sub':
            return elems[-2]

        return 'main'

    def links_in_state(self, state):
        """Return a generator with links in the given state."""
        for link, doc in self._document_iterator(state):
            if link is None:
                yield {}
                continue
            item = {}
            item["url"] = link.url
            item["reason"] = link.reason
            item["lastcheck"] = link.lastcheck
            item["id"] = link.getId
            item["link"] = link.link
            item["document"] = doc
            item["object"] = link.object
            item["owner_mail"] = ""
            item["owner"] = doc.Creator

            yield item

    def _document_iterator(self, state):
        catalog = getToolByName(self.context, 'portal_catalog')
        lc = getToolByName(self.context, 'portal_linkchecker')
        links = lc.database.queryLinks(state=[state], sort_on="url")

        for link in links:
            doc_uid = link.object
            if not doc_uid:
                print "continue, no doc_uid"
                continue
            docs = catalog(
                UID=doc_uid,
                Language='all',
                review_state='published'
            )
            if not len(docs):
                continue
            for doc in docs:
                yield link, doc
