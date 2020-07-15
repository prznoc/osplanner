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
        availability = assigner.filter_workspaces("is_mac", preference, availability, slots, False)
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
        availability = assigner.filter_workspaces("is_mac", preference, availability, slots, False)
        self.assertEqual(availability, expected_availability)


class SelectingSingleWorkspaceTests(TestCase):

    def setUp(self):
        workstation1 = Workstation.objects.create(ws_id = 1)
        workstation1.large_screen = True
        workstation1.is_mac = True
        workstation1.save()
        Workstation.objects.create(ws_id = 2)
        workstation3 = Workstation.objects.create(ws_id = 3)
        workstation3.large_screen = False
        workstation3.is_mac = True
        workstation3.save()
        Preferences.objects.create(user = User.objects.create(name = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 3, large_screen_preference = 2)
        Preferences.objects.create(user = User.objects.create(name = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
    
    def test_filter_favourite_workspace(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday", "saturday"]
        user = User.objects.get(name = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        user.favourite_workspace = workstation1
        user.save()
        schedule = dict.fromkeys(working_days)
        for day in schedule.keys():
            schedule[day] = Workweek.objects.get(workstation = user.favourite_workspace, start_date = next_monday)
        selected_workspace = assigner.assign_next_week(user, working_days)
        self.assertEqual(selected_workspace, schedule)

    def test_matching_workspaces_present(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday", "saturday"]
        user = User.objects.get(name = "Andrzej")
        user.favourite_workspace = None
        user.save()
        workstation1 = Workstation.objects.get(ws_id = 1)
        expected_schedule = dict.fromkeys(working_days)
        for day in expected_schedule.keys():
            expected_schedule[day] = Workweek.objects.get(workstation = workstation1, start_date = next_monday)
        schedule = assigner.assign_next_week(user, working_days)
        self.assertEqual(schedule, expected_schedule)
    
    def test_assign_second_user(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days1 = ["monday", "wednesday", "saturday"]
        working_days2 = ["monday", "tuesday", "friday"]
        user1 = User.objects.get(name = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule1 = assigner.assign_next_week(user1, working_days1)
        expected_schedule1 = dict.fromkeys(working_days1)
        for day in expected_schedule1.keys():
            expected_schedule1[day] = Workweek.objects.get(workstation = workstation1, start_date = next_monday)
        user2 = User.objects.get(name = "Rafał")
        workstation2 = Workstation.objects.get(ws_id = 3)
        schedule2 = assigner.assign_next_week(user2, working_days2)
        expected_schedule2 = dict.fromkeys(working_days2)
        for day in expected_schedule2.keys():
            expected_schedule2[day] = Workweek.objects.get(workstation = workstation2, start_date = next_monday)
        self.assertEqual(schedule1, expected_schedule1)
        self.assertEqual(schedule2, expected_schedule2)
    

    def test_assign_with_1_priority(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday", "saturday"]
        user = User.objects.get(name = "Rafał")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule = assigner.assign_next_week(user, working_days)
        expected_schedule = dict.fromkeys(working_days)
        for day in expected_schedule.keys():
            expected_schedule[day] = Workweek.objects.get(workstation = workstation1, start_date = next_monday)
        self.assertEqual(schedule, expected_schedule)

class SelectingDiffrentWorkspacesTests(TestCase):
    
    def setUp(self):
        workstation1 = Workstation.objects.create(ws_id = 1)
        workstation1.large_screen = True
        workstation1.is_mac = True
        workstation1.save()
        Workstation.objects.create(ws_id = 2)
        Preferences.objects.create(user = User.objects.create(name = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 2)
        Preferences.objects.create(user = User.objects.create(name = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
        
    def test_diffrent_day_assignment(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days1 = ["monday", "wednesday", "saturday"]
        working_days2 = ["monday", "tuesday", "friday"]
        user1 = User.objects.get(name = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule1 = assigner.assign_next_week(user1, working_days1)
        expected_schedule1 = dict.fromkeys(working_days1)
        for day in expected_schedule1.keys():
            expected_schedule1[day] = Workweek.objects.get(workstation = workstation1, start_date = next_monday)
        user2 = User.objects.get(name = "Rafał")
        workstation2 = Workstation.objects.get(ws_id = 2)
        schedule2 = assigner.assign_next_week(user2, working_days2)
        expected_schedule2 = dict.fromkeys(working_days2)
        expected_schedule2["monday"] = Workweek.objects.get(workstation = workstation2, start_date = next_monday)
        expected_schedule2["tuesday"] = Workweek.objects.get(workstation = workstation1, start_date = next_monday)
        expected_schedule2["friday"] = Workweek.objects.get(workstation = workstation1, start_date = next_monday)
        self.assertEqual(schedule1, expected_schedule1)
        self.assertEqual(schedule2, expected_schedule2)
