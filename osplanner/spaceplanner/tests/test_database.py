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
        availability, slots = assigner.prepare_availability(working_days)
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        expected_availability = {}
        for workday in working_days:
            slot1 = Workweek.objects.get(start_date = next_monday, workstation = Workstation.objects.get(ws_id = 1))
            slot2 = Workweek.objects.get(start_date = next_monday, workstation = Workstation.objects.get(ws_id = 2))
            expected_availability[workday] = [slot1, slot2]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(slots, set([slot1, slot2]))

    
    def test_get_slots_after_edition(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slot2 = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        user = User.objects.get(name = "Andrzej")
        slot2.wednesday = user
        slot2.save()
        availability, slots = assigner.prepare_availability(working_days)
        expected_availability = {}
        slot1 = Workweek.objects.get(start_date = next_monday, workstation = Workstation.objects.get(ws_id = 1))
        expected_availability["monday"] = [slot1, slot2]
        expected_availability["wednesday"] = [slot1]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(slots, set([slot1, slot2]))


    def test_get_slots_with_one_empty(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        user = User.objects.get(name = "Andrzej")
        slot.wednesday = user
        slot.monday = user
        slot.save()
        availability, slots = assigner.prepare_availability(working_days)
        expected_availability = {}
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        expected_availability["monday"] = [slot]
        expected_availability["wednesday"] = [slot]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(slots, set([slot]))


class SlotFilteringTest(TestCase):
    def setUp(self):
        Workstation.objects.create(ws_id = 1)
        Workstation.objects.create(ws_id = 2)
        Preferences.objects.create(user = User.objects.create(name = "Andrzej"),
            large_screen = True, is_mac = True)
    
    def test_filter_matching_workspace(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        preference = Preferences.objects.get(user = User.objects.get(name = "Andrzej"))
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1.large_screen = True
        workstation1.is_mac = True
        workstation1.save()
        working_days = ["monday", "wednesday", "saturday"]
        availability, slots = assigner.prepare_availability(working_days)
        availability = assigner.filter_workspaces("is_mac", preference, availability, slots)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation1)
        expected_availability = {}
        for day in working_days:
            expected_availability[day] = [slot]
        self.assertEqual(availability, expected_availability)

    def test_no_matching_workspaces_found(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        user = User.objects.get(name = "Andrzej")
        preference = Preferences.objects.get(user = user)
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        slot.wednesday = user
        slot.monday = user
        slot.save()
        working_days = ["monday", "wednesday"]
        availability, slots = assigner.prepare_availability(working_days)
        expected_availability = availability
        availability = assigner.filter_workspaces("is_mac", preference, availability, slots)
        self.assertEqual(availability, expected_availability)


class SelectingWorkspaceTests(TestCase):

    def setUp(self):
        workstation1 = Workstation.objects.create(ws_id = 1)
        workstation1.large_screen = True
        workstation1.is_mac = True
        workstation1.save()
        Workstation.objects.create(ws_id = 2)
        workstation3 = Workstation.objects.create(ws_id = 3)
        workstation3.large_screen = True
        workstation3.is_mac = True
        workstation3.save()
        Preferences.objects.create(user = User.objects.create(name = "Andrzej"), 
        large_screen = True, is_mac = True)
        user = User.objects.get(name = "Andrzej")
        user.favourite_workspace = workstation1
        user.save()

    def test_filter_favourite_workspace(self):
        working_days = ["monday", "wednesday", "saturday"]
        user = User.objects.get(name = "Andrzej")
        selected_workspace = assigner.assign_next_week(user, working_days)
        self.assertEqual(selected_workspace, user.favourite_workspace)
        