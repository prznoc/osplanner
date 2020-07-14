from datetime import datetime, timedelta

from spaceplanner.models import User, Workweek

def prepare_availability(weekdays):
    next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
    slots = Workweek.objects.filter(start_date = next_monday)
    availability = {}
    for slot in slots:
        free_days = []
        for weekday in weekdays:
            if getattr(slot, weekday) is None:
                free_days.append(weekday)
        if (not free_days): 
            availability[slot] = free_days
    return availability

def assign_next_week(user, weekdays):
    availability = prepare_availability(weekdays)
    pass
'''
    next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
    slots = Workweek.objects.filter(start_date = next_monday)
    availability = {}
    for slot in slots:
        free_days = []
        for weekday in weekdays:
            if getattr(slot, weekday) is None:
                free_days.append(weekday)
        availability[slot] = free_days
    return availability
    '''



        