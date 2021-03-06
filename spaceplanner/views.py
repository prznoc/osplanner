import calendar

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy  as _
from django_tables2 import RequestConfig
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework import mixins
from rest_framework import generics
from rest_framework import permissions
from rest_framework.exceptions import MethodNotAllowed
from django.contrib.auth.models import User

from .models import Userweek, EmployeePreferences, WorkstationPreferences, Workstation, Workweek
from .tables import ScheduleTable, PreferencesTable, WorkstationPreferencesTable
from .app_logic import views_processing
from .forms import UserPreferencesForm, ScheduleForm, WeekdaysForm, UserForm
from .serializers import WorkstationSerializer, WorkstationPreferencesSerializer, EmployeePreferencesSerializer, WorkweekSerializer, UserweekSerializer, UserSerializer
from .permissions import IsOwnerOrAdminOrReadOnly, IsAdminUserOrReadOnly


def home(request):
    return render(request, 'spaceplanner/home.html', {})

@login_required
def edit_information(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            request.user = form.save(commit=False)
            request.user.save()
            return redirect('user_panel')
    else:
        form = UserForm(instance=request.user)
    return render(request, 'spaceplanner/edit_information.html', {'form': form})

@login_required
def user_panel(request, date = None):
    user = request.user
    preferences, created = EmployeePreferences.objects.get_or_create(employee = user)
    preferences = PreferencesTable([preferences])

    if date:
        today = datetime.strptime(date, '%Y-%m')
    else:
        today = datetime.today()
    if today > (datetime.today().replace(day=7) + timedelta(days=31)):
        message = _('Months after the next one are unavailable')
        messages.info(request, message)
        return redirect('user_panel', date=(datetime.today() + timedelta(days=31)).strftime('%Y-%m'))
    try:   
        first_monday = Userweek.objects.all().order_by('monday_date')[0].monday_date
    except IndexError:
        isotoday = datetime.today().isocalendar()
        Userweek.objects.get_or_create(employee=user, year=isotoday[0], week=isotoday[1])
        isotoday = (datetime.today().replace(day=1)).isocalendar()
        Userweek.objects.get_or_create(employee=user, year=isotoday[0], week=isotoday[1])
        first_monday = Userweek.objects.all().order_by('monday_date')[0].monday_date
    if today.date() < first_monday and today.date() < datetime.today().date():
        message = _('Months before databease creation are unavailable')
        messages.info(request, message)
        return redirect('user_panel', date=(first_monday + timedelta(days=7)).strftime('%Y-%m'))

    date = (today + timedelta(days=-today.weekday())).strftime('%Y-%m-%d')
    
    first_monday = today.replace(day=1) + timedelta(days=-today.replace(day=1).weekday())
    last_day = calendar.monthrange(today.year, today.month)[1]
    last_day = today.replace(day=last_day)
    last_monday = last_day + timedelta(days=-last_day.weekday(), weeks=1)
    week_counter = views_processing.generate_nonexistent_userweeks(user, first_monday, last_monday)  # generates userweeks for displayed month and amount of weeks in month

    schedule = Userweek.objects.filter(employee=user).exclude(
            monday_date__lt=first_monday).order_by('monday_date')[:week_counter]
    schedule = Userweek.objects.filter(id__in=schedule)       # filtering for displayed userweeks
    table = ScheduleTable(schedule, order_by=('data_range'))
    RequestConfig(request).configure(table)

    date_name = _(today.strftime('%B')) + ' ' + today.strftime('%Y')
    next_date = (today.replace(day=1) + timedelta(days=31)).strftime('%Y-%m')
    previous_date = (today.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')

    today = datetime.today()
    date = (today + timedelta(days=-today.weekday())).strftime('%Y-%m-%d')

    return render(request, 'spaceplanner/user_panel.html', {'table': table, 'preferences': preferences,
            'date_name': date_name, 'date': date, 'previous_date': previous_date, 'next_date': next_date})

@login_required
def schedule_week(request, pk: int):
    user = request.user
    userweek = get_object_or_404(Userweek, pk=pk)
    monday = userweek.monday_date
    today = datetime.today()
    last_monday = today - timedelta(days=today.weekday())
    if monday < last_monday.date():
        return redirect('workstation_schedule', date=monday.strftime('%Y-%m-%d'))
    this_week_flag = None
    if monday < today.date():
        this_week_flag = True
    date_range = monday.strftime('%Y/%m/%d') + " - " + (monday + timedelta(days=6)).strftime('%Y/%m/%d')
    if request.method == "POST":
        if 'editweek' in request.POST:
            generateform = WeekdaysForm(instance=userweek, flag=this_week_flag)
            editform = ScheduleForm(request.POST, instance=userweek, flag=this_week_flag)
            views_processing.clear_workweek(userweek, list(calendar.day_name))
            if editform.is_valid():
                views_processing.editweek_form_processing(editform, user)
                return redirect('user_panel')
        if 'generateweek' in request.POST:
            editform = ScheduleForm(instance=userweek, flag=this_week_flag)
            generateform = WeekdaysForm(request.POST, instance=userweek, flag=this_week_flag)
            if generateform.is_valid():
                wrong_weekdays = views_processing.generateweek_form_processing(generateform, userweek, user, this_week_flag)
                if wrong_weekdays:
                    message = views_processing.generate_unscheduled_days_message(wrong_weekdays)
                    messages.info(request, message)
                return redirect('user_panel')
        if 'mybtn' in request.POST:
            editform = ScheduleForm(instance=userweek, flag=this_week_flag)
            generateform = WeekdaysForm(instance=userweek, flag=this_week_flag)
            cleared_days = list(calendar.day_name)
            if this_week_flag:
                for weekday in list(calendar.day_name):
                    if list(calendar.day_name).index(weekday) < datetime.today().weekday():
                        cleared_days.remove(weekday)
                    else:
                        break
            views_processing.clear_workweek(userweek, cleared_days)
            views_processing.clear_userweek(userweek, cleared_days)
            return redirect('user_panel')
    else:
        editform = ScheduleForm(instance=userweek, flag=this_week_flag)       
        generateform = WeekdaysForm(instance=userweek,flag=this_week_flag)
    return render(request, 'spaceplanner/schedule_week.html',
            {'userweek': userweek, 'editform': editform, 'generateform': generateform, 'date_range': date_range})

@login_required
def edit_preferences(request):
    user = request.user
    preferences, created = EmployeePreferences.objects.get_or_create(employee=user)
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
def workstation_schedule(request, date:str):
    monday = datetime.strptime(date, '%Y-%m-%d')
    if monday > (datetime.today() + timedelta(days=28) + relativedelta(day=31)):
        message = _('Future schedule is unavailable')
        messages.info(request, message)
        return redirect('workstation_schedule', date= (monday - timedelta(days=7)).strftime('%Y-%m-%d'))
    try:   
        first_monday = Userweek.objects.all().order_by('monday_date')[0].monday_date
    except IndexError:
        isotoday = datetime.today().isocalendar()
        Userweek.objects.get_or_create(employee=request.user, year=isotoday[0], week=isotoday[1])
        first_monday = Userweek.objects.all().order_by('monday_date')[0].monday_date
    if monday.date() < first_monday:
        message = _('Weeks before databease creation are unavailable')
        messages.info(request, message)
        return redirect('workstation_schedule', date= (monday + timedelta(days=7)).strftime('%Y-%m-%d'))
    date_range, table = views_processing.get_schedule_week_table(monday)
    RequestConfig(request).configure(table)
    monday = monday + timedelta(weeks=1)
    next_date = monday.strftime('%Y-%m-%d')
    monday = monday - timedelta(days=14)
    previous_date = monday.strftime('%Y-%m-%d')
    return render(request, 'spaceplanner/workstation_schedule.html',{'table': table, 'date_range': date_range, 'next_date': next_date, 'previous_date': previous_date})

@login_required
def out_of_range(request):
    return render(request, 'spaceplanner/out_of_range.html',{})

@login_required
def workstation_preferences(request):
    data = WorkstationPreferences.objects.all()
    table = WorkstationPreferencesTable(data)
    RequestConfig(request).configure(table)
    return render(request, 'spaceplanner/workstation_preferences.html',{'table':table})

class WorkstationList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Workstation.objects.all()
    serializer_class = WorkstationSerializer

class WorkstationDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Workstation.objects.all()
    serializer_class = WorkstationSerializer


class WorkstationPreferencesList(mixins.ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = WorkstationPreferences.objects.all()
    serializer_class = WorkstationPreferencesSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class WorkstationPreferencesDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = WorkstationPreferences.objects.all()
    serializer_class = WorkstationPreferencesSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    def update(self, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Use PATCH")

    def partial_update(self, request, *args, **kwargs):
        # Override Partial Update Code if desired
        return super().update(*args, **kwargs, partial=True)


class EmployeePreferencesList(mixins.ListModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    queryset = EmployeePreferences.objects.all()
    serializer_class = EmployeePreferencesSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class EmployeePreferencesDetail(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    queryset = EmployeePreferences.objects.all()
    serializer_class = EmployeePreferencesSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="Use PATCH")

    def partial_update(self, request, *args, **kwargs):
        # Override Partial Update Code if desired
        return super().update(*args, **kwargs, partial=True)


class WorkweekList(generics.ListCreateAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Workweek.objects.all()
    serializer_class = WorkweekSerializer
    
class WorkweekDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUserOrReadOnly]
    queryset = Workweek.objects.all()
    serializer_class = WorkweekSerializer


class UserweekList(generics.ListCreateAPIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    queryset = Userweek.objects.all()
    serializer_class = UserweekSerializer

class UserweekDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    queryset = Userweek.objects.all()
    serializer_class = UserweekSerializer


class UserList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)




