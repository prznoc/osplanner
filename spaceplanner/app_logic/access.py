import calendar

from datetime import datetime, timedelta
from django.contrib.auth.models import User

from .assigner import Assigner
from spaceplanner.models import Userweek

class Access():

    def get_week_schedule(user:User, year:int, week:int):
        monday = iso_to_gregorian(year, week, 0)
        userweek = Userweek.objects.get_or_create(employee=user, year=year, week=week)
        schedule = dict()
        for day in list(calendar.day_name):
            schedule[monday] = getattr(userweek, day)
            monday = monday + timedelta(days=1)
        return schedule

    @staticmethod
    def get_three_week_schedule(user:User, weeks_amount: int):
        today = datetime.today()
        calendar = today.isocalendar()
        schedule = self.get_week_schedule(user, calendar[0], calendar[1])
        for i in range(weeks_amount - 1):   
            today = today + timedelta(week=1)
            calendar = today().isocalendar()
            schedule = schedule.update(self.get_week_schedule(user, calendar[0], calendar[1]))
        return schedule
