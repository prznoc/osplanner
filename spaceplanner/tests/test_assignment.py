from django.test import TestCase
from django.contrib.auth.models import User

from spaceplanner.models import Workstation, Workweek, EmployeePreferences, WorkstationPreferences, Userweek
from spaceplanner.app_logic.assigner import Assigner
from spaceplanner.app_logic.views_processing import assign_user_to_workstation


# Hypotesis


class SetupTests(TestCase, Assigner):
 
    def setUp(self):
        Workstation.objects.create(label= 'komp1')
        Workstation.objects.create(label= 'komp2')


    def test_generate_workweeks(self):
        slots1 = self.get_all_slots(3, 2022)
        slots2 = self.get_all_slots(3, 2022)
        self.assertEqual(slots1, slots2)


class AvailabilityTest(TestCase, Assigner):
    def setUp(self):
        Workstation.objects.create(label= 'komp1')
        Workstation.objects.create(label= 'komp2')
        User.objects.create(username = "Andrzej")

    def test_get_free_slots_from_empty_schedule(self):
        working_days = ["Monday", "Wednesday", "Saturday"]
        slots = self.get_all_slots(3, 2022)
        availability, slots = self.prepare_availability(working_days, slots)
        expected_availability = {}
        for workday in working_days:
            slot1 = Workweek.objects.get(week = 3, year = 2022, workstation = Workstation.objects.get(ws_id = 1))
            slot2 = Workweek.objects.get(week = 3, year = 2022, workstation = Workstation.objects.get(ws_id = 2))
            expected_availability[workday] = [slot1, slot2]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(slots, set([slot1, slot2]))

    def test_get_slots_after_edition(self):
        working_days = ["Monday", "Wednesday"]
        slots = self.get_all_slots(3, 2022)
        user = User.objects.get(username = "Andrzej")
        slots[1].Wednesday = user
        slots[1].save()
        availability, available_slots = self.prepare_availability(working_days, slots)
        expected_availability = {}
        expected_availability["Monday"] = [slots[0], slots[1]]
        expected_availability["Wednesday"] = [slots[0]]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(available_slots, set([slots[0], slots[1]]))
    
    def test_get_slots_with_one_empty(self):
        working_days = ["Monday", "Wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slots = self.get_all_slots(3, 2022)
        slot = slots[1]
        user = User.objects.get(username = "Andrzej")
        slot.Wednesday = user
        slot.Monday = user
        slot.save()
        availability, available_slots = self.prepare_availability(working_days, slots)
        expected_availability = {}
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(year=2022, week=3, workstation = workstation)
        expected_availability["Monday"] = [slot]
        expected_availability["Wednesday"] = [slot]
        self.assertEqual(availability, expected_availability)
        self.assertEqual(available_slots, set([slot]))


class SlotFilteringTest(TestCase, Assigner):
    def setUp(self):
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Andrzej"),
            large_screen = True, is_mac = True)
        Workstation.objects.create(label = 'komp1')
        Workstation.objects.create(label = 'komp2')
        Workstation.objects.create(label = 'komp3')
    
    def test_filter_with_three_preferences(self):
        slots = self.get_all_slots(3, 2022)
        preference = EmployeePreferences.objects.get(employee = User.objects.get(username = "Andrzej"))
        workstation1 = Workstation.objects.get(label = 'komp1')
        workstation1_preferences = WorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()
        workstation2 = Workstation.objects.get(label = 'komp2')
        workstation2_preferences = WorkstationPreferences.objects.get(workstation = workstation2)
        workstation2_preferences.large_screen = False
        workstation2_preferences.is_mac = True
        workstation2_preferences.save()
        working_days = ["Monday", "Wednesday", "Saturday"]
        availability, slots = self.prepare_availability(working_days, slots)
        availability = self.filter_workspaces(["is_mac", 'large_screen', 'noise'], preference, availability, slots)
        slot = Workweek.objects.get(year = 2022, week = 3, workstation = workstation1)
        expected_availability = {}
        for day in working_days:
            expected_availability[day] = [slot]
        self.assertEqual(availability, expected_availability)
    
    def test_filter_matching_workspace(self):
        slots = self.get_all_slots(3, 2022)
        preference = EmployeePreferences.objects.get(employee = User.objects.get(username = "Andrzej"))
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = WorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()
        working_days = ["Monday", "Wednesday", "Saturday"]
        availability, slots = self.prepare_availability(working_days, slots)
        availability = self.filter_workspaces(["is_mac"], preference, availability, slots)
        slot = Workweek.objects.get(year = 2022, week = 3, workstation = workstation1)
        expected_availability = {}
        for day in working_days:
            expected_availability[day] = [slot]
        self.assertEqual(availability, expected_availability)

    
    def test_no_matching_workspaces_found(self):
        slots = self.get_all_slots(3, 2022)
        user = User.objects.get(username = "Andrzej")
        preference = EmployeePreferences.objects.get(employee = user)
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(year = 2022, week = 3, workstation = workstation)
        slot.Wednesday = user
        slot.Monday = user
        slot.save()
        working_days = ["Monday", "Wednesday"]
        availability, slots = self.prepare_availability(working_days, slots)
        expected_availability = availability
        availability = self.filter_workspaces(["is_mac"], preference, availability, slots)
        self.assertEqual(availability, expected_availability)


class SelectingSingleWorkspaceTests(TestCase, Assigner):

    def setUp(self):
        Workstation.objects.create(label = '1')
        Workstation.objects.create(label = '2')
        Workstation.objects.create(label = '3')

        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = WorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()

        workstation3 = Workstation.objects.get(ws_id = 3)
        workstation3_preferences = WorkstationPreferences.objects.get(workstation = workstation3)
        workstation3_preferences.large_screen = False
        workstation3_preferences.is_mac = True
        workstation3_preferences.save()

        EmployeePreferences.objects.create(employee = User.objects.create(username = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 3, large_screen_preference = 2)
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Szymon"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
    
    def test_filter_favourite_workspace(self):
        self.get_all_slots(3, 2022)
        working_days = ["Monday", "Wednesday", "Saturday"]
        user = User.objects.get(username = "Andrzej")
        preference = EmployeePreferences.objects.get (employee = user)
        workstation1 = Workstation.objects.get(ws_id = 1)
        preference.favourite_workspace.add(workstation1) 
        preference.save()
        schedule = dict.fromkeys(working_days)
        for day in schedule.keys():
            schedule[day] = Workweek.objects.get(workstation = list(preference.favourite_workspace.all())[0], year = 2022, week = 3)
        selected_workspace = self.assign_week(user, working_days, 3, 2022)
        self.assertEqual(selected_workspace, schedule)
    
    def test_filter_diffrent_favourite_workspaces(self):
        self.get_all_slots(3, 2022)
        working_days = ["Monday", "Wednesday", "Saturday"]
        user = User.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation3 = Workstation.objects.get(ws_id = 3)
        preference = EmployeePreferences.objects.get (employee = user)
        preference.favourite_workspace.add(workstation1) 
        preference.favourite_workspace.add(workstation3) 
        preference.save()

        user2 = User.objects.get(username = "Rafał")
        preference2 = EmployeePreferences.objects.get (employee = user2)
        working_days2 = ["Monday"]
        preference2.favourite_workspace.add(workstation1) 
        preference2.save()
        schedule = self.assign_week(user2, working_days2, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=user2, week=3, year=2022)[0], schedule)

        user3 = User.objects.get(username = "Szymon")
        preference3 = EmployeePreferences.objects.get (employee = user3)
        working_days3 = ["Wednesday"]
        preference3.favourite_workspace.add(workstation3) 
        preference3.save()
        schedule = self.assign_week(user3, working_days3, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=user3, week=3, year=2022)[0], schedule)

        schedule = dict()
        schedule['Monday'] = Workweek.objects.get(workstation = workstation3, year = 2022, week = 3)
        schedule['Wednesday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        schedule['Saturday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        selected_workspace = self.assign_week(user, working_days, 3, 2022)
        self.assertEqual(selected_workspace, schedule)
    
    def test_matching_workspaces_present(self):
        self.get_all_slots(3, 2022)
        working_days = ["Monday", "Wednesday", "Saturday"]
        user = User.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        expected_schedule = dict.fromkeys(working_days)
        for day in expected_schedule.keys():
            expected_schedule[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        schedule = self.assign_week(user, working_days, 3, 2022)
        self.assertEqual(schedule, expected_schedule)
    
    def test_match_with_unavailable_day(self):
        working_days = ["Monday", "Wednesday", "Saturday"]
        schedule = self.assign_week(User.objects.get(username = "Andrzej"), working_days, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=User.objects.get(username = "Andrzej"), week=3, year=2022)[0], schedule)
        schedule = self.assign_week(User.objects.get(username = "Rafał"), working_days, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=User.objects.get(username = "Rafał"), week=3, year=2022)[0], schedule)
        schedule = self.assign_week(User.objects.get(username = "Szymon"), working_days, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=User.objects.get(username = "Szymon"), week=3, year=2022)[0], schedule)
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Stanisław"), 
        large_screen = True, is_mac = True, is_mac_preference = 3, large_screen_preference = 2)
        schedule = self.assign_week(User.objects.get(username = "Stanisław"), ["Monday", "Tuesday", "Friday"], 3, 2022)
        workstation1 = Workstation.objects.get(ws_id = 1)
        expected_schedule = dict()
        expected_schedule['Monday'] = None
        expected_schedule['Tuesday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        expected_schedule['Friday'] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
    
        self.assertEqual(schedule, expected_schedule)

    
    def test_assign_second_user(self):
        working_days1 = ["Monday", "Wednesday", "Saturday"]
        working_days2 = ["Monday", "Tuesday", "Friday"]
        user1 = User.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule1 = self.assign_week(user1, working_days1, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=user1, week=3, year=2022)[0], schedule1)
        expected_schedule1 = dict.fromkeys(working_days1)
        for day in expected_schedule1.keys():
            expected_schedule1[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        user2 = User.objects.get(username = "Rafał")
        workstation2 = Workstation.objects.get(ws_id = 3)
        schedule2 = self.assign_week(user2, working_days2, 3, 2022)
        expected_schedule2 = dict.fromkeys(working_days2)
        for day in expected_schedule2.keys():
            expected_schedule2[day] = Workweek.objects.get(workstation = workstation2, year = 2022, week = 3)
        self.assertEqual(schedule1, expected_schedule1)
        self.assertEqual(schedule2, expected_schedule2)
    
    def test_assign_with_1_priority(self):
        working_days = ["Monday", "Wednesday", "Saturday"]
        user = User.objects.get(username = "Rafał")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule = self.assign_week(user, working_days, 3, 2022)
        expected_schedule = dict.fromkeys(working_days)
        for day in expected_schedule.keys():
            expected_schedule[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        self.assertEqual(schedule, expected_schedule)


class SelectingDiffrentWorkspacesTests(TestCase, Assigner):
    
    def setUp(self):
        Workstation.objects.create(label = '1')
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = WorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = True
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()

        Workstation.objects.create(label = '2')
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 2)
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
        
    def test_diffrent_day_assignment(self):
        working_days1 = ["Monday", "Wednesday", "Saturday"]
        working_days2 = ["Monday", "Tuesday", "Friday"]
        user1 = User.objects.get(username = "Andrzej")
        workstation1 = Workstation.objects.get(ws_id = 1)
        schedule1 = self.assign_week(user1, working_days1, 3, 2022)
        assign_user_to_workstation(Userweek.objects.get_or_create(employee=user1, week=3, year=2022)[0], schedule1)
        expected_schedule1 = dict.fromkeys(working_days1)
        for day in expected_schedule1.keys():
            expected_schedule1[day] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        user2 = User.objects.get(username = "Rafał")
        workstation2 = Workstation.objects.get(ws_id = 2)
        schedule2 = self.assign_week(user2, working_days2, 3, 2022)
        expected_schedule2 = dict.fromkeys(working_days2)
        expected_schedule2["Monday"] = Workweek.objects.get(workstation = workstation2, year = 2022, week = 3)
        expected_schedule2["Tuesday"] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        expected_schedule2["Friday"] = Workweek.objects.get(workstation = workstation1, year = 2022, week = 3)
        self.assertEqual(schedule1, expected_schedule1)
        self.assertEqual(schedule2, expected_schedule2)


class MiscFunctions(TestCase, Assigner):

    def setUp(self):
        Workstation.objects.create(label = '1')
        workstation1 = Workstation.objects.get(ws_id = 1)
        workstation1_preferences = WorkstationPreferences.objects.get(workstation = workstation1)
        workstation1_preferences.large_screen = False
        workstation1_preferences.is_mac = True
        workstation1_preferences.save()

        Workstation.objects.create(label = '2')
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Andrzej"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)
        EmployeePreferences.objects.create(employee = User.objects.create(username = "Rafał"), 
        large_screen = True, is_mac = True, is_mac_preference = 2, large_screen_preference = 1)

    def test_select_matching_workspaces(self):
        preference = EmployeePreferences.objects.get(employee = User.objects.get(username = "Andrzej"))
        workstation1 = Workstation.objects.get(ws_id = 1)
        all_slots = self.get_all_slots(3, 2022)
        availability, slots = self.prepare_availability(["Monday", "Wednesday"], all_slots)
        p = list(availability.values())
        results = set(p[0])
        for s in p[1:]:
            results.intersection_update(s)
        match = self.select_matching_workspace(preference, availability, results, slots)
        self.assertEqual(match, Workweek.objects.get(workstation=workstation1, week=3, year=2022))
    
    
    def test_no_matching_workspaces_found(self):
        preference = EmployeePreferences.objects.get(employee = User.objects.get(username = "Andrzej"))
        workstation1 = Workstation.objects.get(ws_id = 1)
        all_slots = self.get_all_slots(3, 2022)
        availability, slots = self.prepare_availability(["Monday", "Wednesday"], all_slots)
        p = list(availability.values())
        results = set(p[0])
        for s in p[1:]:
            results.intersection_update(s)
        match = self.select_matching_workspace(preference, availability, results, slots)
        self.assertEqual(match, Workweek.objects.get(workstation=workstation1, week=3, year=2022))
