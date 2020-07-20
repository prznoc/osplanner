import calendar

from datetime import datetime, timedelta
from django.contrib.auth.models import User

from .assigner import SGAssigner
from spaceplanner.models import Userweek

class Access():

    def get_week_schedule(user:User, year:int, week:int):
        monday = iso_to_gregorian(year, week, 0)
        userweek = Userweek.objects.get_or_create(employee=user, year=year, week=week)
        for day in list(calendar.day_name):
            schedule[monday] = getattr(userweek, day)
            monday = monday + deltatime(days=1)
        return schedule

    @staticmethod
    def get_three_week_schedule(user:User, weeks_amount: int):
        today = datetime.today()
        calendar = today.isocalendar()
        schedule = get_week_schedule(user, calendar[0], calendar[1])
        for i in range(weeks_amount - 1):   
            today = today + deltatime(week=1)
            calendar = today().isocalendar()
            schedule = schedule.update(get_week_schedule(user, calendar[0], calendar[1]))
        return schedule
