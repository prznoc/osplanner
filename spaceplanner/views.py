from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from spaceplanner.app_logic.access import Access
from django_tables2 import SingleTableView, RequestConfig
from datetime import datetime, timedelta

from .models import Userweek, Workweek
from .tables import ScheduleTable
from .app_logic.assigner import SGAssigner


def generate_nonexistent_userweeks(user, today, weeks_amount):
    for i in range (weeks_amount):
        calendar = today.isocalendar()
        Userweek.objects.get_or_create(employee=user, year=calendar[0], week=calendar[1])
        today = today + timedelta(weeks=1)


def home(request):
    return render(request, 'spaceplanner/home.html', {})


@login_required
def user_panel(request):
    user = request.user
    generate_nonexistent_userweeks(user, datetime.today(), 3)
    last_monday = datetime.today() + timedelta(days=-datetime.today().weekday())
    data = Userweek.objects.filter(employee=user).exclude(monday_date__lt=last_monday).order_by('monday_date')[:3]
    data = Userweek.objects.filter(id__in=data)
    table = ScheduleTable(data)
    RequestConfig(request).configure(table)
    return render(request, 'spaceplanner/user_panel.html', {'table':table})

'''
def schedule_week(request, pk):
    userweek = Userweek.objects.get(pk=pk)
    workweek = Workweek.objects.get_or_create(user=userweek.user, week = userweek.week, year = userweek.year)

    <form action="{% url 'schedule_week'%}" methon='GET'>
<button type="submit">Get Schedule</button>
</form>
    '''
