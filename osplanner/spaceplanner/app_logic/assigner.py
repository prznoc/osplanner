from datetime import datetime, timedelta

from spaceplanner.models import User, Workweek, Preferences

def assign_next_week(user, weekdays):
    next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
    availability, slots = prepare_availability(weekdays)
    results = dict.fromkeys(weekdays, None)
    preferences_set = ["is_mac", "window", "noise", "large_screen"]
    preference = Preferences.objects.get(user = user)
    for preference_name in preferences_set:
        if (getattr(preference, preference_name+"_preference") == 3):
            availability = filter_workspaces(preference_name, preference, availability, slots)
    
    p = list(availability.values())
    results = set(p[0])
    for s in p[1:]:
        results.intersection_update(s)
        slot = Workweek.objects.get(workstation = user.favourite_workspace, start_date = next_monday)
    if slot in results:
        return slot.workstation
    
    for preference_name in preferences_set:
        if (getattr(preference, preference_name+"_preference") == 2):
            availability = filter_workspaces(preference_name, preference, availability, slots)
    
def check_match_all_days(working_weekdays, availability):
    pass 

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
    
def filter_workspaces(preference_name, preference, availability, slots):
    temp_slots = set()
   
    for slot in slots:
        workstation = slot.workstation
        if (getattr(preference, preference_name) == getattr(workstation, preference_name)):
            temp_slots.add(slot)
    
    for day in availability.keys():
        weekday = availability[day]
        new_weekday = [x for x in weekday if x in temp_slots]
        if new_weekday:
            availability[day] = new_weekday

    return availability
    