from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from spaceplanner.app_logic.access import Access
from django_tables2 import SingleTableView, RequestConfig
from datetime import datetime, timedelta
from django.shortcuts import redirect


from .models import Userweek, Workweek, EmployeePreferences
from .tables import ScheduleTable, PreferencesTable
from .app_logic.assigner import SGAssigner
from .forms import UserPreferencesForm


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
    preferences_table = PreferencesTable(preferences)
    RequestConfig(request).configure(table)
    return render(request, 'spaceplanner/user_panel.html', {'table':table, 'preferences':preferences})


def schedule_week(request):
    #userweek = get_object_or_404(Userweek, pk=pk)
    return render(request, 'spaceplanner/schedule_week.html', {})

def edit_preferences(request):
    user = request.user
    preferences = get_object_or_404(EmployeePreferences, employee=user)
    if request.method == "POST":
        form = UserPreferencesForm(request.POST, instance=preferences)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('user_panel')
    else:
        form = UserPreferencesForm(instance=preferences)
    return render(request, 'spaceplanner/edit_preferences.html', {'form': form})
