from django.test import TestCase
from datetime import datetime, timedelta
from django.db import transaction

from spaceplanner.models import User, Workstation, Workweek, Preferences
from spaceplanner.app_logic import assigner

class AvailabilityTest(TestCase):
    def setUp(self):
        Workstation.objects.create(ws_id = 1)
        Workstation.objects.create(ws_id = 2)
        User.objects.create(name = "Andrzej")

    def test_get_free_slots_from_empty_schedule(self):
        working_days = ["monday", "wednesday", "saturday"]
        availability = assigner.prepare_availability(working_days)
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        expected_availability = {}
        for workstation in Workstation.objects.all():
            slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
            expected_availability[slot] = working_days
        self.assertEqual(availability, expected_availability)

    
    def test_get_slots_after_edition(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        user = User.objects.get(name = "Andrzej")
        slot.wednesday = user
        slot.save()
        availability = assigner.prepare_availability(working_days)
        expected_availability = {}
        expected_availability[slot] = ["monday"]
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        expected_availability[slot] = working_days
        self.assertEqual(availability, expected_availability)

    def test_get_slots_with_one_empty(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        user = User.objects.get(name = "Andrzej")
        slot.wednesday = user
        slot.monday = user
        slot.save()
        availability = assigner.prepare_availability(working_days)
        expected_availability = {}
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        expected_availability[slot] = working_days
        self.assertEqual(availability, expected_availability)

class SlotFilteringTest(TestCase):
    def setUp(self):
        Workstation.objects.create(ws_id = 1)
        Workstation.objects.create(ws_id = 2)
        Preferences.objects.create(user = User.objects.create(name = "Andrzej"),
            large_screen = True, is_mac = True)
    
    def test_filter_matching_workspace(self):
        preference = Preferences.objects.get(user = User.objects.get(name = "Andrzej"))
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1.large_screen = True
        workstation1.is_mac = True
        workstation1.save()
        working_days = ["monday", "wednesday", "saturday"]
        availability = assigner.prepare_availability(working_days)
        availability = assigner.filter_workspaces("is_mac", preference, availability)
        expected_availability = {}
        expected_availability[Workweek.objects.get(week_id = 1)] = working_days
        self.assertEqual(availability, expected_availability)

    def test_no_matching_workspaces_found(self):
        preference = Preferences.objects.get(user = User.objects.get(name = "Andrzej"))
        working_days = ["monday", "wednesday", "saturday"]
        availability = assigner.prepare_availability(working_days)
        expected_availability = availability
        availability = assigner.filter_workspaces("is_mac", preference, availability)
        self.assertEqual(availability, expected_availability)


        