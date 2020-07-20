import django_tables2 as tables
from .models import Userweek, EmployeePreferences
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

    class Meta:
        model = EmployeePreferences