from django.contrib import admin
from .models import Workstation, Employee, Workweek

admin.site.register(Workstation)
admin.site.register(Employee)
admin.site.register(Workweek)