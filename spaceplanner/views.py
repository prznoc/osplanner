import calendar

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from spaceplanner.app_logic.access import Access
from django_tables2 import SingleTableView, RequestConfig
from datetime import datetime, timedelta
from django.shortcuts import redirect


from .models import Userweek, Workweek, EmployeePreferences, Workstation
from .tables import ScheduleTable, PreferencesTable
from .app_logic.assigner import Assigner
from .forms import UserPreferencesForm, ScheduleForm, WeekdaysForm


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
    preferences = EmployeePreferences.objects.filter(employee = user)
    generate_nonexistent_userweeks(user, datetime.today(), 3)
    last_monday = datetime.today() + timedelta(days=-datetime.today().weekday())
    data = Userweek.objects.filter(employee=user).exclude(monday_date__lt=last_monday).order_by('monday_date')[:3]
    data = Userweek.objects.filter(id__in=data)
    table = ScheduleTable(data)
    RequestConfig(request).configure(table)
    return render(request, 'spaceplanner/user_panel.html', {'table':table, 'preferences':preferences})


#usuwanie rekordów z workweek nie działa po włożeniu do if form.is_valid():
@login_required
def schedule_week(request, pk):
    user = request.user
    userweek = get_object_or_404(Userweek, pk=pk)
    if request.method == "POST":
        if 'editweek' in request.POST:
            editform = ScheduleForm(request.POST, instance=userweek)
            print(editform.instance)
            clear_workweek(userweek)
            if editform.is_valid():
                userweek = editform.save(commit=False)
                for weekday in list(calendar.day_name):
                    workstation = getattr(userweek, weekday)
                    if workstation:
                        workweek, created = Workweek.objects.get_or_create(workstation = workstation, week = userweek.week, year = userweek.year)
                        setattr(workweek, weekday, user)
                        workweek.save()
                generateform = WeekdaysForm()
                userweek.save()
                return redirect('user_panel')
        if 'generateweek' in request.POST:
            generateform = WeekdaysForm(request.POST)
            if generateform.is_valid():
                weekdays = generateform.cleaned_data.get('weekdays')
                clear_workweek(userweek)
                clear_userweek(userweek)
                assigner = Assigner()
                assigner.assign_week(user,weekdays,userweek.week, userweek.year)
                editform = ScheduleForm(instance=userweek)
                return redirect('user_panel')  
    else:
        editform = ScheduleForm(instance=userweek)        
        generateform = WeekdaysForm()
    return render(request, 'spaceplanner/schedule_week.html', {'userweek': userweek, 'editform': editform, 'generateform': generateform})

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

def clear_workweek(userweek):
    for weekday in list(calendar.day_name):
        workstation = getattr(userweek, weekday)
        if workstation:
            workweek, created = Workweek.objects.get_or_create(workstation = workstation, week = userweek.week, year = userweek.year)
            setattr(workweek, weekday, None)
            workweek.save()

def clear_userweek(userweek):
    for weekday in list(calendar.day_name):
        setattr(userweek, weekday, None)
        userweek.save()