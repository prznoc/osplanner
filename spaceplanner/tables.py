import django_tables2 as tables
import calendar

from django.utils.translation import ugettext_lazy  as _

from .models import Userweek, EmployeePreferences, Workweek, WorkstationPreferences
from datetime import datetime, timedelta

class WeekdayColumn(tables.Column):
    def render(self, value, record, column):
        today = datetime.today()
        today_weekday = list(calendar.day_name)[today.weekday()]
        today = today.isocalendar()
        if getattr(record, 'year') == today[0] and \
            getattr(record, 'week') == today[1] and \
                self.verbose_name == _(today_weekday):
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
            record.date=record.monday_date.strftime('%Y-%m-%d')
            self.template_name = 'spaceplanner/view_button.html'
        else: self.template_name = 'spaceplanner/schedule_button.html'
        return super(ScheduleButtonColumn, self).render(record, table, value, bound_column, **kwargs)


class ScheduleTable(tables.Table):
    data_range = tables.Column(accessor='monday_date', verbose_name=_('Dates'))
    year=tables.Column(orderable=False)
    week=tables.Column(orderable=False)
    generate_schedule = ScheduleButtonColumn(
            template_name= 'spaceplanner/view_button.html',
            orderable=False,
            verbose_name=_('Generate schedule')
            )

    def render_data_range(self, record):
        return record.monday_date.strftime('%Y/%m/%d') + " - " + (record.monday_date + timedelta(days=6)).strftime('%Y/%m/%d')
 
    def __init__(self, *args, **kwargs):
        for weekday in list(calendar.day_name):
            self.base_columns[weekday] = WeekdayColumn(accessor=weekday, orderable=False, empty_values=[],
                    verbose_name=_(weekday))
        super().__init__(*args, **kwargs)


    class Meta:
        template_name = "django_tables2/bootstrap.html"
        exclude = ['monday_date', 'id', 'employee']
        sequence = ['data_range', '...']
        model = Userweek


class PreferencesTable(tables.Table):

    favourite_list = tables.Column(accessor='favourite_workspace', verbose_name=_('Favourite Workspaces'))

    def render_favourite_list(self, record):
        return ', '.join([str(a) for a in record.favourite_workspace.all()])
    
    class Meta:
        exclude = ('id', 'employee')
        model = EmployeePreferences

class WorkstationPreferencesTable(tables.Table):

    class Meta:
        model = WorkstationPreferences
        exclude = ['id']


class WorkstationWeekdayColumn(tables.Column):
    def render(self, value, record, column):
        today = datetime.today()
        today_weekday = list(calendar.day_name)[today.weekday()]
        today = today.isocalendar()
        if getattr(record, 'year') == today[0] and \
            getattr(record, 'week') == today[1] and \
                self.verbose_name == _(today_weekday):
                    self.attrs = {'td': {'class': 'today'}}
        else:
            column.attrs = {'td': {}}
        if not value:
            return '---'
        return value.get_full_name


class WorkstationsScheduleTable(tables.Table):

    workstation = tables.Column(verbose_name=_("Workstation"), accessor = 'workstation.label')
    
    def __init__(self, *args, **kwargs):
        for weekday in list(calendar.day_name):
            self.base_columns[weekday] = WorkstationWeekdayColumn(accessor=weekday, orderable=False, empty_values=[],
                    verbose_name=_(weekday))
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = Workweek
        exclude = ['week_id', 'year', 'week']