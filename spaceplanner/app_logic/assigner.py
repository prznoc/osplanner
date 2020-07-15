from datetime import datetime, timedelta
from statistics import mode
import random

from spaceplanner.models import User, Workweek, Preferences

def assign_next_week(user, weekdays: list):   #typowanie listy
    next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
    availability, slots = prepare_availability(weekdays)  #availability - weekdays with free slots
    schedule = dict.fromkeys(weekdays) #returned schedule
    preferences_set = ["is_mac", "window", "noise", "large_screen"]
    preference = Preferences.objects.get(user = user)
    for preference_name in preferences_set:         
        if (getattr(preference, preference_name+"_preference") == 3):
            availability = filter_workspaces(preference_name, preference, availability, slots, False)
    p = list(availability.values())     #uwaga na pustą listę
    results = set(p[0])   #available slots
    for s in p[1:]:
        results.intersection_update(s)
    try:
        #przydzielać jeśli jest chociaż jeden dzień
        slot = Workweek.objects.get(workstation = user.favourite_workspace, start_date = next_monday)
        if slot in results:
            for day in schedule.keys():
                schedule[day] = slot
            assign_user_to_workstation(user, schedule)
            return schedule
    except:
        pass

    for preference_name in preferences_set:
        if (getattr(preference, preference_name+"_preference") == 2):
            availability = filter_workspaces(preference_name, preference, availability, slots, False)
    p = list(availability.values())
    results = set(p[0])
    for s in p[1:]:
        results.intersection_update(s)
    if len(results) == 1:
        chosen_slot = results.pop()
        for day in schedule.keys():
            schedule[day] = chosen_slot
        assign_user_to_workstation(user, schedule)
        return schedule 
    if len(results) > 1:
        for day in weekdays:
            availability[day] = list(results.intersection(availability[day]))
        chosen_slot = select_matching_workspace(preference, availability, results)
        for day in schedule.keys():
            schedule[day] = chosen_slot
        assign_user_to_workstation(user, schedule)
        return schedule
    if not results:
        for day in schedule.keys():
            schedule[day] = match_slot_to_day(preference, day, availability, preferences_set)
        assign_user_to_workstation(user, schedule)
        return schedule
           
def match_slot_to_day(preference, day, availability, preferences_set):
    possible_slots = availability[day]
    for preference_name in preferences_set:
        if (getattr(preference, preference_name+"_preference") == 1):
            temp_slots = []
            for slot in possible_slots:
                workstation = slot.workstation
                if (getattr(preference, preference_name) == getattr(workstation, preference_name)):
                    temp_slots.append(slot)
            if temp_slots:
                possible_slots = temp_slots
    return possible_slots[0]
    
def select_matching_workspace(preference, availability, results):
    preferences_set = ["is_mac", "window", "noise", "large_screen"] # wsadzić od razu do listy
    for preference_name in preferences_set:
        if (getattr(preference, preference_name+"_preference") == 1):
            availability = filter_workspaces(preference_name, preference, availability, results, True)
    slots_list = [item for sublist in availability.values() for item in sublist]
    if not slots_list:
        return results[0]
    else: 
        return mode(slots_list)
    
def assign_user_to_workstation(user, schedule):
    for day in schedule.keys():
        setattr(schedule[day], day, user)
    schedule[day].save()

def prepare_availability(weekdays):
    next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
    slots = Workweek.objects.filter(start_date = next_monday)
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
    
def filter_workspaces(preference_name, preference, availability, slots, empty_permission_flag):
    temp_slots = set()
   
    for slot in slots:
        workstation = slot.workstation
        if (getattr(preference, preference_name) == getattr(workstation, preference_name)):
            temp_slots.add(slot)
    
    for day in availability.keys():        
        weekday = availability[day]
        new_weekday = [x for x in weekday if x in temp_slots]     
        if new_weekday or empty_permission_flag:    #returns slots matching preferences
            availability[day] = new_weekday

    return availability
    