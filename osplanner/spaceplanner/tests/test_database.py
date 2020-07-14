from django.test import TestCase
from datetime import datetime, timedelta

from spaceplanner.models import User, Workstand, Workweek
from spaceplanner.app_logic import assigner

class DatabaseTests(TestCase):
    def setUp(self):
        Workstand.objects.create(ws_id = 1)
        Workstand.objects.create(ws_id = 2)

    def test_get_free_workstands_slots(self):
        working_days = ["monday", "wednesday", "saturday"]
        availability = assigner.prepare_availability(working_days)
        #print(availability)
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        wanted_availability = {}
        for workstand in Workstand.objects.all():
            slot = Workweek.objects.get(start_date = next_monday, workstand = workstand)
            wanted_availability[slot] = working_days
        #print(wanted_availability)
        self.assertEqual(availability, wanted_availability)
