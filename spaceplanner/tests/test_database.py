from django.test import TestCase
from datetime import datetime, timedelta
from django.db import transaction

from spaceplanner.models import Employee, Workstation, Workweek, SGEmployeePreferences, SGWorkstationPreferences
from spaceplanner.app_logic.assigner import SGAssigner


#Hypotesis

class SetupTests(TestCase, SGAssigner):
    
    def setUp(self):
        Workstation.objects.create(ws_id = 1)
        Workstation.objects.create(ws_id = 2)
    
    def test_generate_workweeks(self):
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation2 = Workstation.objects.get(ws_id = 2)
        slots1, created1 = self.get_all_slots(3, 2022)
        slots2, created2 = self.get_all_slots(3, 2022)
        self.assertEqual(slots1, slots2)
        self.assertEqual(created1, True)
        self.assertEqual(created2, False)


class AvailabilityTest(TestCase, SGAssigner):
    def setUp(self):
        Workstation.objects.create(ws_id = 1)
        Workstation.objects.create(ws_id = 2)
        Employee.objects.create(username = "Andrzej")
    
    def test_get_free_slots_from_empty_schedule(self):
        working_days = ["monday", "wednesday", "saturday"]
        slots, created = self.get_all_slots(3, 2022)
        availability, slots = self.prepare_availability(working_days, slots)
        expected_availability = {}
        for workday in working_days:
            slot1 = Workweek.objects.get(week = 3, year = 2022, workstation = Workstation.objects.get(ws_id = 1))
            slot2 = Workweek.objects.get(week = 3, year = 2022, workstation = Workstation.objects.get(ws_id = 2))
            expected_availability[workday] = [slot1, slot2]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(slots, set([slot1, slot2]))
    
    #ask for reference error
    def test_get_slots_after_edition(self):
        working_days = ["monday", "wednesday"]
        slots, created = self.get_all_slots(3, 2022)
        workstation = Workstation.objects.get(ws_id = 2)
        user = Employee.objects.get(username = "Andrzej")
        slots[1].wednesday = user
        slots[1].save()
        availability, available_slots = self.prepare_availability(working_days, slots)
        expected_availability = {}
        expected_availability["monday"] = [slots[0], slots[1]]
        expected_availability["wednesday"] = [slots[0]]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(available_slots, set([slots[0], slots[1]]))
    
    
    def test_get_slots_with_one_empty(self):
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slots, created = self.get_all_slots(3, 2022)
        slot = slots[1]
        user = Employee.objects.get(username = "Andrzej")
        slot.wednesday = user
        slot.monday = user
        slot.save()
        availability, available_slots = self.prepare_availability(working_days, slots)
        expected_availability = {}
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(year=2022, week=3, workstation = workstation)
        expected_availability["monday"] = [slot]
        expected_availability["wednesday"] = [slot]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(available_slots, set([slot]))


class SlotFilteringTest(TestCase, SGAssigner):
    def setUp(self):
        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Andrzej"),
            large_screen = True, is_mac = True)
        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 1))
        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 2))
    
    def test_filter_matching_workspace(self):
        slots, created = self.get_all_slots(3, 2022)
        preference = SGEmployeePreferences.objects.get(employee = Employee.objects.get(username = "Andrzej"))
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = SGWorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()
        working_days = ["monday", "wednesday", "saturday"]
        availability, slots = self.prepare_availability(working_days, slots)
        availability = self.filter_workspaces("is_mac", preference, availability, slots, False)
        slot = Workweek.objects.get(year = 2022, week = 3, workstation = workstation1)
        expected_availability = {}
        for day in working_days:
            expected_availability[day] = [slot]
        self.assertEqual(availability, expected_availability)


    def test_no_matching_workspaces_found(self):
        slots, created = self.get_all_slots(3, 2022)
        user = Employee.objects.get(username = "Andrzej")
        preference = SGEmployeePreferences.objects.get(employee = user)
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(year = 2022, week = 3, workstation = workstation)
        slot.wednesday = user
        slot.monday = user
        slot.save()
        working_days = ["monday", "wednesday"]
        availability, slots = self.prepare_availability(working_days, slots)
        expected_availability = availability
        availability = self.filter_workspaces("is_mac", preference, availability, slots, False)
        self.assertEqual(availability, expected_availability)


class SelectingSingleWorkspaceTests(TestCase, SGAssigner):

    def setUp(self):
        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 1))
        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 2))
        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 3))

        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = SGWorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()

        workstation3 = Workstation.objects.get(ws_id = 3)
        workstation3_preferences = SGWorkstationPreferences.objects.get(workstation = workstation3)
        workstation3_preferences.large_screen = False
        workstation3_preferences.is_mac = True
        workstation3_preferences.save()

        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 3, large_screen_preference = 2)
        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Szymon"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
    
    def test_filter_favourite_workspace(self):
        slots, created = self.get_all_slots(3, 2022)
        working_days = ["monday", "wednesday", "saturday"]
        user = Employee.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        user.favourite_workspace.add(workstation1) 
        user.save()
        schedule = dict.fromkeys(working_days)
        for day in schedule.keys():
            schedule[day] = Workweek.objects.get(workstation = list(user.favourite_workspace.all())[0], year = 2022, week = 3)
        selected_workspace = self.assign_week(user, working_days, 3, 2022)
        self.assertEqual(selected_workspace, schedule)

    def test_filter_diffrent_favourite_workspaces(self):
        slots, created = self.get_all_slots(3, 2022)
        working_days = ["monday", "wednesday", "saturday"]
        user = Employee.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation3 = Workstation.objects.get(ws_id = 3)
        user.favourite_workspace.add(workstation1) 
        user.favourite_workspace.add(workstation3) 
        user.save()

        user2 = Employee.objects.get(username = "Rafał")
        working_days2 = ["monday"]
        user2.favourite_workspace.add(workstation1) 
        user2.save()
        self.assign_week(user2, working_days2, 3, 2022)

        user3 = Employee.objects.get(username = "Szymon")
        working_days3 = ["wednesday"]
        user3.favourite_workspace.add(workstation3) 
        user3.save()
        self.assign_week(user3, working_days3, 3, 2022)

        schedule = dict()
        schedule['monday'] = Workweek.objects.get(workstation = workstation3, year = 2022, week = 3)
        schedule['wednesday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        schedule['saturday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        selected_workspace = self.assign_week(user, working_days, 3, 2022)
        self.assertEqual(selected_workspace, schedule)
    
    def test_matching_workspaces_present(self):
        slots, created = self.get_all_slots(3, 2022)
        working_days = ["monday", "wednesday", "saturday"]
        user = Employee.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        expected_schedule = dict.fromkeys(working_days)
        for day in expected_schedule.keys():
            expected_schedule[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        schedule = self.assign_week(user, working_days, 3, 2022)
        self.assertEqual(schedule, expected_schedule)
    
    def test_match_with_unavailable_day(self):
        working_days = ["monday", "wednesday", "saturday"]
        self.assign_week(Employee.objects.get(username = "Andrzej"), working_days, 3, 2022)
        self.assign_week(Employee.objects.get(username = "Rafał"), working_days, 3, 2022)
        self.assign_week(Employee.objects.get(username = "Szymon"), working_days, 3, 2022)
        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Stanisław"), 
        large_screen = True, is_mac = True, is_mac_preference = 3, large_screen_preference = 2)
        schedule = self.assign_week(Employee.objects.get(username = "Stanisław"), ["monday", "tuesday", "friday"], 3, 2022)
        workstation1 = Workstation.objects.get(ws_id = 1)
        expected_schedule = dict()
        expected_schedule['monday'] = None
        expected_schedule['tuesday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        expected_schedule['friday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        self.assertEqual(schedule, expected_schedule)

    
    def test_assign_second_user(self):
        working_days1 = ["monday", "wednesday", "saturday"]
        working_days2 = ["monday", "tuesday", "friday"]
        user1 = Employee.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule1 = self.assign_week(user1, working_days1, 3, 2022)
        expected_schedule1 = dict.fromkeys(working_days1)
        for day in expected_schedule1.keys():
            expected_schedule1[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        user2 = Employee.objects.get(username = "Rafał")
        workstation2 = Workstation.objects.get(ws_id = 3)
        schedule2 = self.assign_week(user2, working_days2, 3, 2022)
        expected_schedule2 = dict.fromkeys(working_days2)
        for day in expected_schedule2.keys():
            expected_schedule2[day] = Workweek.objects.get(workstation = workstation2, year = 2022, week = 3)
        self.assertEqual(schedule1, expected_schedule1)
        self.assertEqual(schedule2, expected_schedule2)
    
    def test_assign_with_1_priority(self):
        working_days = ["monday", "wednesday", "saturday"]
        user = Employee.objects.get(username = "Rafał")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule = self.assign_week(user, working_days, 3, 2022)
        expected_schedule = dict.fromkeys(working_days)
        for day in expected_schedule.keys():
            expected_schedule[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        self.assertEqual(schedule, expected_schedule)


class SelectingDiffrentWorkspacesTests(TestCase, SGAssigner):
    
    def setUp(self):
        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 1))
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = SGWorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()

        SGWorkstationPreferences.objects.create(workstation = Workstation.objects.create(ws_id = 2))
        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 2)
        SGEmployeePreferences.objects.create(employee = Employee.objects.create(username = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
        
    def test_diffrent_day_assignment(self):
        working_days1 = ["monday", "wednesday", "saturday"]
        working_days2 = ["monday", "tuesday", "friday"]
        user1 = Employee.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule1 = self.assign_week(user1, working_days1, 3, 2022)
        expected_schedule1 = dict.fromkeys(working_days1)
        for day in expected_schedule1.keys():
            expected_schedule1[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        user2 = Employee.objects.get(username = "Rafał")
        workstation2 = Workstation.objects.get(ws_id = 2)
        schedule2 = self.assign_week(user2, working_days2, 3, 2022)
        expected_schedule2 = dict.fromkeys(working_days2)
        expected_schedule2["monday"] = Workweek.objects.get(workstation = workstation2, year = 2022, week = 3)
        expected_schedule2["tuesday"] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        expected_schedule2["friday"] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        self.assertEqual(schedule1, expected_schedule1)
        self.assertEqual(schedule2, expected_schedule2)
