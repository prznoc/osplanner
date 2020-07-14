from datetime import datetime, timedelta

from spaceplanner.models import User, Workweek, Preferences

def prepare_availability(weekdays):
    next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
    slots = Workweek.objects.filter(start_date = next_monday)
    availability = {}
    for slot in slots:
        free_days = []
        for weekday in weekdays:
            if getattr(slot, weekday) is None:
                free_days.append(weekday)
        if (free_days): 
            availability[slot] = free_days
    return availability

def assign_next_week(user, weekdays):
    availability = prepare_availability(weekdays)
    preferences_set = ["is_mac", "window", "noise", "large_screen"]
    preference = Preferences.objects.get(user == user)
    for preference_name in preferences_set:
        if (getattr(preference, preference_name+"_preference") == 3):
            availability = filter_workspaces(preference_name, preference, availability)
    
def filter_workspaces(preference_name, preference, availability):
    new_availability = {}
    slots = availability.keys()
    for slot in slots:
        workstation = slot.workstation
        if (getattr(preference, preference_name) == getattr(workstation, preference_name)):
            new_availability[slot] = availability[slot]
    if new_availability: return new_availability
    else: return availability
