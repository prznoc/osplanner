import calendar

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django_tables2 import SingleTableView, RequestConfig
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from datetime import datetime, timedelta

from .models import Userweek, Workweek, EmployeePreferences, Workstation
from .tables import ScheduleTable, PreferencesTable, WorkstationsScheduleTable
from .app_logic.assigner import Assigner
from .forms import UserPreferencesForm, ScheduleForm, WeekdaysForm


def generate_nonexistent_userweeks(user, first_monday, last_monday)->int:
    week_counter = 0
    while first_monday != last_monday:
        calendar = first_monday.isocalendar()
        Userweek.objects.get_or_create(employee=user, year=calendar[0], week=calendar[1])
        for workstation in Workstation.objects.all():
            Workweek.objects.get_or_create(workstation= workstation, year=calendar[0], week=calendar[1])
        first_monday = first_monday + timedelta(weeks=1)
        week_counter = week_counter + 1
    return week_counter


def home(request):
    return render(request, 'spaceplanner/home.html', {})

@login_required
def user_panel(request, date=''):
    user = request.user
    preferences, created  = EmployeePreferences.objects.get_or_create(employee = user)
    preferences = PreferencesTable([preferences])

    if date:   
        today = datetime.strptime(date, '%Y-%m')
    else: today = datetime.today()
    date = (today + timedelta(days=-today.weekday())).strftime('%Y-%m-%d')
    
    first_monday = today.replace(day=1) + timedelta(days=-today.replace(day=1).weekday())
    last_day = calendar.monthrange(today.year, today.month)[1]
    last_day = today.replace(day=last_day)
    last_monday = last_day + timedelta(days=-last_day.weekday(), weeks=1)
    week_counter = generate_nonexistent_userweeks(user, first_monday, last_monday)  #generates userweeks for displayed month and amount of weeks in month

    schedule = Userweek.objects.filter(employee=user).exclude(
            monday_date__lt=first_monday).order_by('monday_date')[:week_counter]
    schedule = Userweek.objects.filter(id__in=schedule)       #filtering for displayed userweeks
    table = ScheduleTable(schedule, order_by=('data_range'))  
    RequestConfig(request).configure(table)

    date_name = today.strftime('%B') + ' ' +today.strftime('%Y')
    next_date = (today.replace(day=1) + timedelta(days=31)).strftime('%Y-%m')
    previous_date = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

    return render(request, 'spaceplanner/user_panel.html', {'table':table, 'preferences':preferences, 
            'date_name': date_name, 'date':date, 'previous_date':previous_date, 'next_date':next_date})


'''
class ScheduleWeekView(TemplateView):

    editform_class = UserPreferencesForm
    generateform_class = ScheduleForm
    template_name = 'spaceplanner/schedule_week.html'

    def get(self, request, pk):
        userweek = get_object_or_404(Userweek, pk=pk)
        generateform = WeekdaysForm(self.request.GET or None)
        editform = ScheduleForm(self.request.GET or None, instance=userweek)
        context = {'userweek': userweek, 'editform': editform, 'generateform': generateform}
        return self.render_to_response(context)
'''


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
                editweek_form_processing(editform, user)
                return redirect('user_panel')
        if 'generateweek' in request.POST:
            editform = ScheduleForm(instance=userweek)
            generateform = WeekdaysForm(request.POST)
            if generateform.is_valid():
                generateweek_form_processing(generateform, userweek, user)
                return redirect('user_panel')  
        if 'mybtn' in request.POST:
            editform = ScheduleForm(instance=userweek)
            generateform = WeekdaysForm() 
            clear_workweek(userweek)
            clear_userweek(userweek)
            return redirect('user_panel')  
    else:
        editform = ScheduleForm(instance=userweek)       
        generateform = WeekdaysForm()
    return render(request, 'spaceplanner/schedule_week.html', 
            {'userweek': userweek, 'editform': editform, 'generateform': generateform})

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

def generateweek_form_processing(generateform, userweek, user):
    weekdays = generateform.cleaned_data.get('weekdays')
    clear_workweek(userweek)
    clear_userweek(userweek)
    assigner = Assigner()
    assigner.assign_week(user,weekdays,userweek.week, userweek.year)
    for weekday in weekdays:
        if not getattr(userweek, weekday):
            pass

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

@login_required
def workstation_schedule(request, date):
    monday = datetime.strptime(date, '%Y-%m-%d')
    date_range, table = get_schedule_week_table(monday)
    monday = monday + timedelta(weeks=1)
    next_date = monday.strftime('%Y-%m-%d')
    monday = monday - timedelta(days=14)
    previous_date = monday.strftime('%Y-%m-%d')
    return render(request, 'spaceplanner/workstation_schedule.html',{'table': table, 'date_range': date_range, 'next_date': next_date, 'previous_date': previous_date})

def get_schedule_week_table(monday):
    workstations = Workstation.objects.all()
    isocalendar = monday.isocalendar()
    date_range = monday.strftime('%Y/%m/%d') + " - " + (monday + timedelta(days=6)).strftime('%Y/%m/%d') + ", " + str(isocalendar[1]) + '|' + str(isocalendar[0])
    data = [Workweek.objects.get_or_create(workstation=x, week=isocalendar[1], year=isocalendar[0])[0] for x in workstations]
    table = WorkstationsScheduleTable(data)
    return date_range, table
