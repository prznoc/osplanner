import calendar

from datetime import datetime, timedelta

from spaceplanner.models import Userweek, Workweek, Workstation
from spaceplanner.app_logic.assigner import Assigner
from spaceplanner.tables import WorkstationsScheduleTable

def generate_nonexistent_userweeks(user, first_monday, last_monday) -> int:
    week_counter = 0
    while first_monday != last_monday:
        calendar = first_monday.isocalendar()
        Userweek.objects.get_or_create(employee=user, year=calendar[0], week=calendar[1])
        for workstation in Workstation.objects.all():
            Workweek.objects.get_or_create(workstation=workstation, year=calendar[0], week=calendar[1])
        first_monday = first_monday + timedelta(weeks=1)
        week_counter = week_counter + 1
    return week_counter

def editweek_form_processing(editform, user):
    userweek = editform.save(commit=False)
    for weekday in list(calendar.day_name):
        workstation = getattr(userweek, weekday)
        if workstation:
            workweek, created = Workweek.objects.get_or_create(
                    workstation = workstation, week = userweek.week, year = userweek.year)
            if not getattr(workweek, weekday):
                setattr(workweek, weekday, user)
                workweek.save()
            else:
                setattr(userweek, weekday, None)
        userweek.save()

def generateweek_form_processing(generateform, userweek: Userweek, user, this_week_flag:bool):
    weekdays = generateform.cleaned_data.get('weekdays')
    schedule = dict()
    cleared_days = list(calendar.day_name)
    if this_week_flag:
        for weekday in list(calendar.day_name):
            if list(calendar.day_name).index(weekday) < datetime.today().weekday():
                cleared_days.remove(weekday)
            else:
                break
    clear_workweek(userweek, list(cleared_days))
    clear_userweek(userweek, list(cleared_days))
    assigner = Assigner()
    schedule = assigner.assign_week(user, weekdays, userweek.week, userweek.year)
    wrong_weekdays = assign_user_to_workstation(userweek, schedule)
    return wrong_weekdays

def generate_unscheduled_days_message(wrong_weekday: list):
    message = "Following days could not be scheduled: "
    for day in wrong_weekday:
        message = message + day + ", "
    message = message[:-2]
    return message

def assign_user_to_workstation(userweek, schedule: dict()):
    user = userweek.employee
    wrong_weekdays = []
    for day in schedule.keys():
        if schedule[day]:
            setattr(schedule[day], day, user)
            setattr(userweek, day, schedule[day].workstation)
            userweek.save()
            schedule[day].save()
        else: 
            wrong_weekdays.append(day)
    return wrong_weekdays

def clear_workweek(userweek, cleared_days: list):
    for weekday in cleared_days:
        workstation = getattr(userweek, weekday)
        if workstation:
            workweek, created = Workweek.objects.get_or_create(workstation = workstation,
                    week = userweek.week, year = userweek.year)
            setattr(workweek, weekday, None)
            workweek.save()

def clear_userweek(userweek, cleared_days: list):
    for weekday in cleared_days:
        setattr(userweek, weekday, None)
        userweek.save()

def get_schedule_week_table(monday):
    workstations = Workstation.objects.all()
    isocalendar = monday.isocalendar()
    date_range = monday.strftime('%Y/%m/%d') + " - " + (monday + timedelta(days=6)).strftime('%Y/%m/%d') + ", " + str(isocalendar[1]) + '|' + str(isocalendar[0])
    data = [Workweek.objects.get_or_create(workstation=x, week=isocalendar[1], year=isocalendar[0])[0] for x in workstations]
    table = WorkstationsScheduleTable(data)
    return date_range, table
