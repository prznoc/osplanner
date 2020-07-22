from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

from .models import Workstation, Workweek, Userweek, EmployeePreferences, WorkstationPreferences

class UnitInlineWorkstation(admin.TabularInline):
    model = WorkstationPreferences

class UnitInlineEmployee(admin.TabularInline):
    model = EmployeePreferences

class CustomerAdminWorkstation(admin.ModelAdmin):
    inlines = [UnitInlineWorkstation]

class CustomerAdminEmployee(AuthUserAdmin):
    inlines = [UnitInlineEmployee,]


admin.site.unregister(User)
admin.site.register(User, CustomerAdminEmployee)
admin.site.register(Workstation, CustomerAdminWorkstation)
admin.site.register(Workweek)
admin.site.register(Userweek)
admin.site.register(EmployeePreferences)
admin.site.register(WorkstationPreferences)
