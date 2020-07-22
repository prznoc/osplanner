import django_tables2 as tables
from .models import Userweek, EmployeePreferences, Workweek
from django_tables2.utils import A
from datetime import datetime, timedelta

class ScheduleTable(tables.Table):
    data_range = tables.Column(accessor='monday_date', verbose_name='dates', linkify=("schedule_week", (tables.A("pk"), )))
    Monday = tables.Column(orderable = False)
    Tuesday = tables.Column(orderable = False)
    Wednesday = tables.Column(orderable = False)
    Thursday = tables.Column(orderable = False)
    Friday = tables.Column(orderable = False)
    Saturday = tables.Column(orderable = False)
    Sunday = tables.Column(orderable = False)
    '''
    generate_schedule = tables.TemplateColumn(
        template_name="spaceplanner/schedule_button.html", verbose_name="Get schedule", orderable=False)
    '''

    def render_data_range(self, record):
        return record.monday_date.strftime('%Y/%m/%d') + " - " + (record.monday_date + timedelta(days=6)).strftime('%Y/%m/%d')

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        fields = ['data_range' ,'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                'Saturday', 'Sunday']
        model = Userweek

class PreferencesTable(tables.Table):

    #user = tables.Column(accessor='employee', verbose_name='Empolyee')
    favourite_list = tables.Column(accessor='favourite_workspace', verbose_name='Favourite Workspaces')

    '''
    def render_user(self, record):
        return record.employee.first_name + ' ' + record.employee.last_name
    '''

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