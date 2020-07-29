import django_tables2 as tables
import calendar

from .models import Userweek, EmployeePreferences, Workweek
from django.shortcuts import render
from django_tables2.utils import A
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe

class WeekdayColumn(tables.Column):
    def render(self, value, record, column):
        today = datetime.today()
        today_weekday = list(calendar.day_name)[today.weekday()]
        today = today.isocalendar()
        if getattr(record, 'year') == today[0] and \
            getattr(record, 'week') == today[1] and \
                self.verbose_name == today_weekday:
                    self.attrs = {'td': {'class': 'today'}}
        else:
            column.attrs = {'td': {}}
        if not value:
            return '---'
        return value


class ScheduleButtonColumn(tables.TemplateColumn):
    def render(self, record, table, value, bound_column, **kwargs):
        last_monday = (datetime.today() - timedelta(days=datetime.today().weekday())).date()
        if (record.monday_date < last_monday):
            self.template_code = '<a class="btn btn-primary" href="{% url "schedule_week" record.pk %}">View Schedule</a>'
        else: self.template_code = '<a class="btn btn-primary" href="{% url "schedule_week" record.pk %}">Schedule Week</a>'
        return super(ScheduleButtonColumn, self).render(record, table, value, bound_column, **kwargs)


class ScheduleTable(tables.Table):
    data_range = tables.Column(accessor='monday_date', verbose_name='Dates')
    year=tables.Column(orderable=False)
    week=tables.Column(orderable=False)
    generate_schedule = ScheduleButtonColumn('<a class="btn btn-primary" href="{% url "schedule_week" record.pk %}">Schedule Week</a>', orderable=False)

    def render_data_range(self, record):
        return record.monday_date.strftime('%Y/%m/%d') + " - " + (record.monday_date + timedelta(days=6)).strftime('%Y/%m/%d')
 
    def __init__(self, *args, **kwargs):
        for weekday in list(calendar.day_name):
            self.base_columns[weekday] = WeekdayColumn(accessor=weekday, orderable=False, empty_values=[],
                    verbose_name=weekday)
        super().__init__(*args, **kwargs)


    class Meta:
        template_name = "django_tables2/bootstrap.html"
        exclude = ['monday_date', 'id', 'employee']
        sequence = ['data_range', '...']
        model = Userweek


class PreferencesTable(tables.Table):

    favourite_list = tables.Column(accessor='favourite_workspace', verbose_name='Favourite Workspaces')

    def render_favourite_list(self, record):
        return ', '.join([str(a) for a in record.favourite_workspace.all()])
    
    class Meta:
        exclude = ('id', 'employee')
        model = EmployeePreferences


class WorkstationWeekdayColumn(tables.Column):
    def render(self, value, record, column):
        today = datetime.today()
        today_weekday = list(calendar.day_name)[today.weekday()]
        today = today.isocalendar()
        if getattr(record, 'year') == today[0] and \
            getattr(record, 'week') == today[1] and \
                self.verbose_name == today_weekday:
                    self.attrs = {'td': {'class': 'today'}}
        else:
            column.attrs = {'td': {}}
        if not value:
            return '---'
        return value.get_full_name


class WorkstationsScheduleTable(tables.Table):

    workstation = tables.Column(verbose_name="Workstation ID", accessor = 'workstation.ws_id')
    
    def __init__(self, *args, **kwargs):
        for weekday in list(calendar.day_name):
            self.base_columns[weekday] = WorkstationWeekdayColumn(accessor=weekday, orderable=False, empty_values=[],
                    verbose_name=weekday)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Workweek
        exclude = ['week_id', 'year', 'week']