from django.test import TestCase
from datetime import datetime, timedelta

from spaceplanner.models import User, Workstation, Workweek
from spaceplanner.app_logic import assigner

class DatabaseTests(TestCase):
    def setUp(self):
        Workstation.objects.create(ws_id = 1)
        Workstation.objects.create(ws_id = 2)
        User.objects.create(name = "Andrzej")

    def test_get_free_slots_from_empty_schedule(self):
        working_days = ["monday", "wednesday", "saturday"]
        availability = assigner.prepare_availability(working_days)
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        wanted_availability = {}
        for workstation in Workstation.objects.all():
            slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
            wanted_availability[slot] = working_days
        self.assertEqual(availability, wanted_availability)

    
    def test_get_slots_after_edition(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        user = User.objects.get(name = "Andrzej")
        slot.wednesday = user
        slot.save()
        availability = assigner.prepare_availability(working_days)
        wanted_availability = {}
        wanted_availability[slot] = ["monday"]
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        wanted_availability[slot] = working_days
        self.assertEqual(availability, wanted_availability)

    def test_get_slots_with_one_empty(self):
        next_monday = datetime.today() + timedelta(days=-datetime.today().weekday(), weeks=1)
        working_days = ["monday", "wednesday"]
        workstation = Workstation.objects.get(ws_id = 2)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        user = User.objects.get(name = "Andrzej")
        slot.wednesday = user
        slot.monday = user
        slot.save()
        availability = assigner.prepare_availability(working_days)
        wanted_availability = {}
        workstation = Workstation.objects.get(ws_id = 1)
        slot = Workweek.objects.get(start_date = next_monday, workstation = workstation)
        wanted_availability[slot] = working_days
        self.assertEqual(availability, wanted_availability)
        