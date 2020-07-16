from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext as _

from composite_field import CompositeField

from datetime import datetime, timedelta

class Workstation(models.Model):
    ws_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.ws_id)

class WorkstationPreferences(models.Model):
    workstation = models.ForeignKey(Workstation, name=_('workstation'), on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SGWorkstationPreferences(WorkstationPreferences):
    window = models.BooleanField(_('window'), default=False)
    noise = models.BooleanField(_('noise'), default=False)
    large_screen = models.BooleanField(_('large_screen'), default=False)
    is_mac = models.BooleanField(_('is_mac'), default=False)


class Employee(models.Model):
    us_id = models.AutoField(primary_key=True)
    username = models.CharField(_('username'), max_length=200)
    favourite_workspace = models.ManyToManyField(Workstation)   #name in manytomany

    def __str__(self):
        return str(self.username)
    

class EmployeePreferences(models.Model):
    employee = models.ForeignKey(Employee, name=_("employee"), on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SGEmployeePreferences(EmployeePreferences):
    window = models.BooleanField(_('window'), default = False)
    window_preference = models.IntegerField(_('window_preference'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])
    noise = models.BooleanField(_('noise'), default = False)
    noise_preference = models.IntegerField(_('noise_preference'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])
    large_screen = models.BooleanField(_('large_screen'), default = False)
    large_screen_preference = models.IntegerField(_('large_screen_preference'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])
    is_mac = models.BooleanField(_('is_mac'), default = False)
    is_mac_preference = models.IntegerField(_('is_mac_preference'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])


class DateField(CompositeField):
    year = models.IntegerField(_('year'))
    week = models.IntegerField(_('week'))

class Workweek(models.Model):
    week_id = models.AutoField(primary_key=True)
    workstation = models.ForeignKey(Workstation, name=_("workstation"), on_delete=models.CASCADE)
    date = models.DateField() 
    monday = models.ForeignKey(Employee, name=_("monday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= "monday")
    tuesday = models.ForeignKey(Employee, name=_("tuesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name="tuesday")
    wednesday = models.ForeignKey(Employee, name=_("wednesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'wednesday')
    thursday = models.ForeignKey(Employee, name=_("thursday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'thursday')
    friday = models.ForeignKey(Employee, name=_("friday"), blank = True, null = True,
            on_delete=models.SET_NULL, related_name = 'friday')
    saturday = models.ForeignKey(Employee, name=_("saturday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'saturday')
    sunday = models.ForeignKey(Employee, name=_("sunday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'sunday')

    def __str__(self):
        return str(str(self.workstation) + str(self.start_date) + str(self.week_id))

    class Meta:
        unique_together = ('workstation', 'date')
