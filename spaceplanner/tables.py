import django_tables2 as tables
from .models import Userweek
from django_tables2.utils import A
from datetime import datetime, timedelta

class ScheduleTable(tables.Table):
    data_range = tables.Column(accessor='monday_date', verbose_name='dates')
    monday = tables.Column(orderable = False)
    tuesday = tables.Column(orderable = False)
    wednesday = tables.Column(orderable = False)
    thursday = tables.Column(orderable = False)
    friday = tables.Column(orderable = False)
    saturday = tables.Column(orderable = False)
    sunday = tables.Column(orderable = False)
    generate_schedule = tables.TemplateColumn(
        template_name="spaceplanner/schedule_button.html", verbose_name="Get schedule", orderable=False)

    def render_data_range(self, record):
        return record.monday_date.strftime('%Y/%m/%d') + " - " + (record.monday_date + timedelta(days=6)).strftime('%Y/%m/%d')

    class Meta:
        template_name = "django_tables2/bootstrap.html"
        fields = ['data_range' ,'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                'saturday', 'sunday']
        model = Userweek