from datetime import datetime, timedelta
from statistics import mode
from abc import ABC, abstractmethod
from django.contrib.auth.models import User

from spaceplanner.models import Workweek, EmployeePreferences, Workstation, WorkstationPreferences, Userweek


class Assigner():

    preferences_set = ["is_mac", "window", "noise", "large_screen"]

    def assign_week(self, user: User, weekdays: list, week_number: int, year: int) -> dict:
        if not weekdays: return  #jakoś blokować pustą listę
        all_slots, created = self.get_all_slots(week_number, year)
        availability, slots = self.prepare_availability(weekdays, all_slots)
        schedule = dict.fromkeys(weekdays) #schedule to return
        preference = EmployeePreferences.objects.get(employee = user)
        # None for days with no matching workstation
        temp_weekdays = weekdays.copy()
        for day in temp_weekdays:
            if not availability[day]:
                weekdays.remove(day)
                availability.pop(day, None)
            if not weekdays:
                self.assign_user_to_workstation(user, schedule, week_number, year)
                return schedule

        # return favourite if matching all days
        for preference_name in self.preferences_set:         
            if (getattr(preference, preference_name+"_preference") == 3):
                availability = self.filter_workspaces(preference_name, preference, availability, slots, False)
        p = list(availability.values())
        results = set(p[0])
        for s in p[1:]:
            results.intersection_update(s) #workstations available on all days
        try:
            favourites = preference.favourite_workspace.all()
            favourites = [Workweek.objects.get(workstation = x, year = year, week = week_number) for x in favourites]
            common = list(set(results).intersection(favourites))
            if common:
                for day in weekdays:
                    schedule[day] = common[0]
                self.assign_user_to_workstation(user, schedule, week_number, year)
                return schedule
        except:
            pass

        #assign favourites to days with one
        #może zmienić algorytm żeby liczył pasującę
        try:
            favourites = preferences.favourite_workspace.all()
            favourites = [Workweek.objects.get(workstation = x, year = year, week = week_number) for x in favourites]
            temp_weekdays = weekdays.copy()
            for day in temp_weekdays:
                common = list(set(availability[day]).intersection(favourites))
                if common:
                    schedule[day] = common[0]
                    weekdays.remove(day)
                    availability.pop(day, None)
            if not weekdays:
                self.assign_user_to_workstation(user, schedule, week_number, year)
                return schedule
        except:
            pass

        #assign one workspace matching with priority 2
        for preference_name in self.preferences_set:         
            if (getattr(preference, preference_name+"_preference") == 2):
                availability = self.filter_workspaces(preference_name, preference, availability, slots, False)

        p = list(availability.values())
        results = set(p[0])
        for s in p[1:]:
            results.intersection_update(s)
        if len(results) == 1:            #if one matching, match
            chosen_slot = results.pop()
            for day in weekdays:
                schedule[day] = chosen_slot
            self.assign_user_to_workstation(user, schedule, week_number, year)
            return schedule 
        if len(results) > 1:             #if more than one matching, match most suitable with priority 1
            for day in weekdays:
                availability[day] = list(results.intersection(availability[day]))
            chosen_slot = self.select_matching_workspace(preference, availability, results)
            for day in weekdays:
                schedule[day] = chosen_slot
            self.assign_user_to_workstation(user, schedule, week_number, year)
            return schedule
        if not results:                  #if none matching, select separatly for each day
            for day in weekdays:
                schedule[day] = self.match_slot_to_day(preference, day, availability)
            self.assign_user_to_workstation(user, schedule, week_number, year)
            return schedule

    def assign_next_week(self, user: User, weekdays: list) -> dict:
        week_after_today = datetime.today() + timedelta (days = 7)
        week_number = week_after_today.isocalendar()[1]
        year = week_after_today.isocalendar()[0]
        return self.assign_week(user, weekdays, week_number, year)

    def get_all_slots(self, week_number: int, year: int) -> [list, bool]:
        slots = []
        for station in Workstation.objects.all():
            slot, created = Workweek.objects.get_or_create(workstation=station ,year = year, 
                        week = week_number)
            slots.append(slot)
        return slots, created
        
    def prepare_availability(self, weekdays: list, slots: list):
        availability = {}
        free_slots = set()
        for weekday in weekdays:
            free_workstations = []
            for slot in slots:
                if getattr(slot, weekday) is None:
                    free_workstations.append(slot)
                    free_slots.add(slot)
            availability[weekday] = free_workstations
        return availability, free_slots

    def assign_user_to_workstation(self, user, schedule, week, year):
        userweek, created = Userweek.objects.get_or_create(employee = user, week = week, year = year)
        for day in schedule.keys():
            if schedule[day]:
                setattr(schedule[day], day, user)
                setattr(userweek, day, schedule[day].workstation)
                userweek.save()
                schedule[day].save()

    def filter_workspaces(self, preference_name, preference, availability, slots, empty_permission_flag):
        temp_slots = set()
   
        for slot in slots:
            workstation = slot.workstation
            workstation_preference = WorkstationPreferences.objects.get(workstation = workstation)
            if (getattr(preference, preference_name) == getattr(workstation_preference, preference_name)):
                temp_slots.add(slot)
    
        for day in availability.keys():        
            weekday = availability[day]
            new_weekday = [x for x in weekday if x in temp_slots]     
            if new_weekday or empty_permission_flag:    #returns slots matched to preferences
                availability[day] = new_weekday
        return availability

    def select_matching_workspace(self, preference, availability, results):
        for preference_name in self.preferences_set:
            if (getattr(preference, preference_name+"_preference") == 1):
                availability = self.filter_workspaces(preference_name, preference, availability, results, True)
        slots_list = [item for sublist in availability.values() for item in sublist]
        if not slots_list:
            return results[0]
        else: 
            return mode(slots_list)
   
    def match_slot_to_day(self, preference, day, availability):
        possible_slots = availability[day]
        for preference_name in self.preferences_set:
            if (getattr(preference, preference_name+"_preference") == 1):
                temp_slots = []
                for slot in possible_slots:
                    workstation = slot.workstation
                    workstation_preference = WorkstationPreferences.objects.get(workstation = workstation)
                    if (getattr(preference, preference_name) == getattr(workstation_preference, preference_name)):
                        temp_slots.append(slot)
                if temp_slots:
                    possible_slots = temp_slots
        return possible_slots[0]