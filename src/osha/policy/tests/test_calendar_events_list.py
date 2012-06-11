import unittest2 as unittest
from ordereddict import OrderedDict
from datetime import date
from dateutil.relativedelta import relativedelta

from DateTime import DateTime
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login

from osha.policy.tests.base import OSHA_INTEGRATION_TESTING, startZServerSSH


def get_relative_week(relative_weeks):
    relative_week = date.today() + relativedelta(weeks = relative_weeks)
    relative_week_str = relative_week.strftime("%x UTC")
    return DateTime(relative_week_str)


class TestCalendarEventsListViews(unittest.TestCase):

    layer = OSHA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.workflow = self.portal.portal_workflow

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

        self.portal.invokeFactory("Topic", "eventscollection")
        events_folder = self.portal.events

        next_week = get_relative_week(1)
        past_week = get_relative_week(-1)

        events_folder.invokeFactory("Event", "future_event")
        events_folder.future_event.setStartDate(next_week)

        events_folder.invokeFactory("Event", "outdated_event")
        outdated_event = events_folder.outdated_event
        outdated_event.outdated = True
        outdated_event.setStartDate(past_week)

        events_folder.invokeFactory("Event", "tbc_event")
        tbc_event = events_folder.tbc_event
        tbc_event.dateToBeConfirmed = True
        tbc_event.setStartDate(next_week)

        events_folder.invokeFactory("Event", "past_event")
        past_event = events_folder.past_event
        past_event.setStartDate(past_week)

        for i in events_folder.objectIds():
            event = events_folder[i]
            self.workflow.doActionFor(event, 'publish')
            event.reindexObject()

    def test_events_get_events_folder(self):
        folder = self.portal.events
        view = folder.unrestrictedTraverse("@@events.html")
        events = view.get_events()
        event_ids = sorted([i.getId for i in events])
        self.assertEquals(event_ids, ["future_event", "tbc_event"])

    def test_past_get_events_folder(self):
        folder = self.portal.events
        view = folder.unrestrictedTraverse("@@past_events.html")
        events = view.get_events()
        event_ids = sorted([i.getId for i in events])
        self.assertEquals(event_ids, ["outdated_event", "past_event"])

    # def test_events_collection_list(self):
    #     collection = self.portal.eventscollection
    #     view = collection.unrestrictedTraverse("@@events.html")

    # def test_past_events_collection_list(self):
    #     collection = self.portal.eventscollection
    #     view = collection.unrestrictedTraverse("@@past_events.html")


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
