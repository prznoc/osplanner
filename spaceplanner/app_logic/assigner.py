import calendar

from datetime import datetime, timedelta
from statistics import mode
from abc import ABC, abstractmethod
from django.contrib.auth.models import User
from collections import Counter

from spaceplanner.models import Workweek, EmployeePreferences, Workstation, WorkstationPreferences, Userweek

class Assigner():

    preferences_set = ["is_mac", "window", "noise", "large_screen"]

    def assign_week(self, user: User, weekdays: list, week_number: int, year: int) -> dict:
        if not weekdays: return dict() # return empty dictionary with empty list 
        all_slots = self.get_all_slots(week_number, year)      #List of all WORKWEEKS matching week and year
        availability, slots = self.prepare_availability(weekdays, all_slots)     #Availability is {Weekday: slot}
        schedule = dict.fromkeys(weekdays) #schedule to return
        preference, created = EmployeePreferences.objects.get_or_create(employee = user)

        # None for days with no free slot
        temp_weekdays = weekdays.copy()
        for day in temp_weekdays:
            if not availability[day]:
                weekdays.remove(day)
                availability.pop(day, None)
        if not weekdays:
            return schedule

        # match preference 3, return favourite if matching all days
        preference_names = [x for x in self.preferences_set if getattr(preference, x+"_preference") == 3]
        if preference_names:
            availability = self.filter_workspaces(preference_names, preference, availability, slots)    #filter slots by preference
        p = list(availability.values())
        results = set(p[0])
        for s in p[1:]:
            results.intersection_update(s)      #slots available on all days
        favourites = preference.favourite_workspace.all()
        if favourites:
            favourites = [Workweek.objects.get(workstation = x, year = year, week = week_number) for x in favourites]
            common = list(set(results).intersection(favourites))        #List of slots both available on all days and in favourites
            if common:
                for day in weekdays:
                    schedule[day] = common[0]
                return schedule

        #assign favourites to days with one
        favourites = preference.favourite_workspace.all()
        if favourites:
            favourites = [Workweek.objects.get(workstation = x, year = year, week = week_number) for x in favourites]
            previous_day = None
            for day in list(calendar.day_name):     #iteration to keep same workstation on consecutive days if possible
                if day in availability.keys():
                    common = list(set(availability[day]).intersection(favourites))
                    if common:
                        if schedule.get(previous_day) in common:
                            schedule[day] = schedule.get(previous_day)
                        else:
                            schedule[day] = common[0]
                        weekdays.remove(day)
                        availability.pop(day, None)
                previous_day=day
            if not weekdays:
                return schedule

        #find workspaces with priority 2
        preference_names = [x for x in self.preferences_set if getattr(preference, x+"_preference") == 2]
        if preference_names:
            availability = self.filter_workspaces(preference_names, preference, availability, slots)

        p = list(availability.values())     
        results = set(p[0])
        for s in p[1:]:                  #slots matching all days
            results.intersection_update(s)
        if len(results) == 1:            #if one matching, match
            chosen_slot = results.pop()
            for day in weekdays:
                schedule[day] = chosen_slot
            return schedule 
        if len(results) > 1:             #if more than one matching, match most suitable with priority 1
            for day in weekdays:
                availability[day] = list(results.intersection(availability[day]))
            chosen_slot = self.select_matching_workspace(preference, availability, results, slots)
            for day in weekdays:
                schedule[day] = chosen_slot
            return schedule
        if not results:                  #if none matching, select separatly for each day
            preference_names = [x for x in self.preferences_set if getattr(preference, x+"_preference") == 1]       #pytanie czy chcę w takim wypadku filtrować z 1
            if preference_names:
                availability = self.filter_workspaces(preference_names, preference, availability, slots)
            previous_day = None
            for day in list(calendar.day_name):
                if day in availability.keys():
                    if schedule.get(previous_day) in availability[day]:
                        schedule[day] = schedule.get(previous_day)
                    else: schedule[day] = availability[day][0]
                previous_day=day
            return schedule

    def get_all_slots(self, week_number: int, year: int) -> list:
        slots = []
        for station in Workstation.objects.all():
            slot, created = Workweek.objects.get_or_create(workstation=station ,year = year, 
                        week = week_number)
            slots.append(slot)
        return slots
        
    def prepare_availability(self, weekdays: list, slots: list) -> [dict, set]:
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

    def most_frequent_elements(self, test_list:list):    #replace with statistics.multimode(list) in Python 3.8
        res = [] 
        test_list1 = Counter(test_list)  
        temp = test_list1.most_common(1)[0][1]  
        for ele in test_list: 
            if test_list.count(ele) == temp: 
                res.append(ele) 
        res = list(set(res)) 
        return res

    def filter_workspaces(self, preference_names: list, preference: EmployeePreferences, availability: dict, slots: list) -> dict:
        matching_slots = []
        for preference_name in preference_names:
            temp_slots = []
            for slot in slots:
                workstation = slot.workstation
                workstation_preference, created = WorkstationPreferences.objects.get_or_create(workstation = workstation)
                if (getattr(preference, preference_name) == getattr(workstation_preference, preference_name)):
                    temp_slots.append(slot)
            matching_slots = matching_slots + temp_slots
        if matching_slots:
            temp_slots = self.most_frequent_elements(matching_slots)        #replace in python 3.8 (statistics.multimode())
            for day in availability.keys():        
                weekday = availability[day]
                new_weekday = [x for x in weekday if x in temp_slots]     
                if new_weekday:    #returns slots matched to preferences
                    availability[day] = new_weekday
        return availability

    def select_matching_workspace(self, preference: EmployeePreferences, availability: dict, results: set, slots: set) -> Workweek:
        preference_names = [x for x in self.preferences_set if getattr(preference, x+"_preference") == 1]
        if preference_names:
            availability = self.filter_workspaces(preference_names, preference, availability, slots)
        slots_list = [item for sublist in availability.values() for item in sublist]    #decompose 2-dimensional list to 1-dimensional list
        if not slots_list:
            results = list(results)
            return results[0]
        else:      
            return max(set(slots_list), key = slots_list.count)     # change to 'return mode(slots_list)' after migration to python 3.8
   