from django.contrib import admin
from .models import Workstation, Workweek, Userweek, EmployeePreferences, WorkstationPreferences

admin.site.register(Workstation)
admin.site.register(Workweek)
admin.site.register(Userweek)
admin.site.register(EmployeePreferences)
admin.site.register(WorkstationPreferences)