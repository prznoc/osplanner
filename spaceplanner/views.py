import calendar

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_tables2 import SingleTableView, RequestConfig
from datetime import datetime, timedelta
from django.shortcuts import redirect

from .models import Userweek, Workweek, EmployeePreferences, Workstation
from .tables import ScheduleTable, PreferencesTable, WorkstationsScheduleTable
from .app_logic.assigner import Assigner
from .forms import UserPreferencesForm, ScheduleForm, WeekdaysForm


def generate_nonexistent_userweeks(user, today, weeks_amount):
    for i in range (weeks_amount):
        calendar = today.isocalendar()
        Userweek.objects.get_or_create(employee=user, year=calendar[0], week=calendar[1])
        today = today + timedelta(weeks=1)


def home(request):
    return render(request, 'spaceplanner/home.html', {})

#preferencje w adminie od strony workstation
#wyświetlić week number
#labele do wszystkiego
#widok miesiąca
@login_required
def user_panel(request):
    user = request.user
    preferences = EmployeePreferences.objects.filter(employee = user)
    preferences = PreferencesTable(preferences)
    generate_nonexistent_userweeks(user, datetime.today(), 3)
    last_monday = datetime.today() + timedelta(days=-datetime.today().weekday())
    data = Userweek.objects.filter(employee=user).exclude(
            monday_date__lt=last_monday).order_by('monday_date')[:3]
    data = Userweek.objects.filter(id__in=data)
    table = ScheduleTable(data)
    RequestConfig(request).configure(table)
    return render(request, 'spaceplanner/user_panel.html', {'table':table, 'preferences':preferences})

#rozdzielić na 2 formy
@login_required
def schedule_week(request, pk):
    user = request.user
    userweek = get_object_or_404(Userweek, pk=pk)
    if request.method == "POST":
        if 'editweek' in request.POST:
            generateform = WeekdaysForm()
            editform = ScheduleForm(request.POST, instance=userweek)
            clear_workweek(userweek)
            if editform.is_valid():
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
                return redirect('user_panel')
        if 'generateweek' in request.POST:
            editform = ScheduleForm(instance=userweek)
            generateform = WeekdaysForm(request.POST)
            if generateform.is_valid():
                weekdays = generateform.cleaned_data.get('weekdays')
                clear_workweek(userweek)
                clear_userweek(userweek)
                assigner = Assigner()
                assigner.assign_week(user,weekdays,userweek.week, userweek.year)
                return redirect('user_panel')  
    else:
        editform = ScheduleForm(instance=userweek)        
        generateform = WeekdaysForm()
    return render(request, 'spaceplanner/schedule_week.html', 
            {'userweek': userweek, 'editform': editform, 'generateform': generateform})

def clear_workweek(userweek):
    for weekday in list(calendar.day_name):
        workstation = getattr(userweek, weekday)
        if workstation:
            workweek, created = Workweek.objects.get_or_create(workstation = workstation, 
                    week = userweek.week, year = userweek.year)
            setattr(workweek, weekday, None)
            workweek.save()

def clear_userweek(userweek):
    for weekday in list(calendar.day_name):
        setattr(userweek, weekday, None)
        userweek.save()


@login_required
def edit_preferences(request):
    user = request.user
    preferences = get_object_or_404(EmployeePreferences, employee=user)
    if request.method == "POST":
        form = UserPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            preferences = form.save(commit=False)
            preferences.save()
            return redirect('user_panel')
    else:
        form = UserPreferencesForm(instance=preferences)
    return render(request, 'spaceplanner/edit_preferences.html', {'form': form})

def workstation_schedule(request):
    monday = datetime.today() + timedelta(days=-datetime.today().weekday())
    date_range, table = render_schedule_week_table(monday)
    if(request.GET.get('mybtn')):
        monday = monday + timedelta(days = 7)
        date_range, table = render_schedule_week_table(monday)
        return redirect('workstation_schedule')
    return render(request, 'spaceplanner/workstation_schedule.html',{'table': table, 'date_range': date_range})

def render_schedule_week_table(monday):
    workstations = Workstation.objects.all()
    isocalendar = monday.isocalendar()
    date_range = monday.strftime('%Y/%m/%d') + " - " + (monday + timedelta(days=6)).strftime('%Y/%m/%d')
    data = [Workweek.objects.get_or_create(workstation=x, week=isocalendar[1], year=isocalendar[0])[0] for x in workstations]
    table = WorkstationsScheduleTable(data)
    return date_range, table
