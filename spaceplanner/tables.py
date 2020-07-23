import django_tables2 as tables
import calendar

from .models import Userweek, EmployeePreferences, Workweek
from django_tables2.utils import A
from datetime import datetime, timedelta


class ScheduleTable(tables.Table):
    data_range = tables.Column(accessor='monday_date', verbose_name='dates', linkify=("schedule_week", (tables.A("pk"), )))
    #jeśli chcę guzik trzeba manualnie zdefiniować url w szablonie
    '''
    generate_schedule = tables.TemplateColumn(
        template_name="spaceplanner/schedule_button.html", verbose_name="Get schedule", orderable=False)
    '''

    def render_data_range(self, record):
        return record.monday_date.strftime('%Y/%m/%d') + " - " + (record.monday_date + timedelta(days=6)).strftime('%Y/%m/%d')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today_weekday = list(calendar.day_name)[datetime.today().weekday()]
        for weekday in list(calendar.day_name):
            self.base_columns[weekday].orderable = False
        #self.week = datetime.today().isocalendar()[1]
        #self.base_columns[today_weekday].attrs={'td': {'bgcolor': 'lightgreen'}}

    '''
    def render_Thursday(self, value, record, column):
        today_week = datetime.today().isocalendar()[1]
        if getattr(record, 'week') == self.week:
            column.attrs = {'td': {'bgcolor': 'lightblue'}}
        else:
            column.attrs = {'td': {}}
        return value
    '''
    
    
    class Meta:
        template_name = "django_tables2/bootstrap.html"
        fields = ['data_range' ,'year','week','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                'Saturday', 'Sunday']
        model = Userweek


class PreferencesTable(tables.Table):

    favourite_list = tables.Column(accessor='favourite_workspace', verbose_name='Favourite Workspaces')

    def render_favourite_list(self, record):
        return ', '.join([str(a) for a in record.favourite_workspace.all()])
    
    class Meta:
        exclude = ('id', 'employee')
        model = EmployeePreferences


class WorkstationsScheduleTable(tables.Table):

    workstation = tables.Column(verbose_name="Workstation ID")

    class Meta:
        model = Workweek
        fields = ['workstation','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                'Saturday', 'Sunday']