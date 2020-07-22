from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext as _
from django.conf import settings
from datetime import datetime, timedelta

from .app_logic import calendar_functions

class Workstation(models.Model):
    ws_id = models.IntegerField(primary_key=True)

    def __str__(self):
        return str(self.ws_id)


class WorkstationPreferences(models.Model):
    workstation = models.OneToOneField(Workstation, name=_('workstation'), on_delete=models.CASCADE)
    window = models.BooleanField(_('window'), default=False)
    noise = models.BooleanField(_('noise'), default=False)
    large_screen = models.BooleanField(_('large_screen'), default=False)
    is_mac = models.BooleanField(_('is_mac'), default=False)


class EmployeePreferences(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, name=_("employee"), on_delete=models.CASCADE)
    favourite_workspace = models.ManyToManyField(Workstation, name=_("favourite_workspace"), default = None) 
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


class Workweek(models.Model):
    week_id = models.AutoField(primary_key=True)
    workstation = models.ForeignKey(Workstation, name=_("workstation"), on_delete=models.CASCADE)
    year =  models.IntegerField(_('year'))
    week = models.IntegerField(_('week'))
    Monday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Monday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= "Monday")
    Tuesday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Tuesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name="Tuesday")
    Wednesday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Wednesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Wednesday')
    Thursday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Thursday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Thursday')
    Friday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Friday"), blank = True, null = True,
            on_delete=models.SET_NULL, related_name = 'Friday')
    Saturday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Saturday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Saturday')
    Sunday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("Sunday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Sunday')

    def __str__(self):
        return str(str(self.workstation) + str(self.year)+ str(self.week))

    class Meta:
        unique_together = ('workstation', 'year', 'week')

class Userweek(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("employee"), on_delete=models.CASCADE)
    year =  models.IntegerField(_('year'))
    week = models.IntegerField(_('week'))
    monday_date = models.DateField(_("monday_date"))
    monday = models.ForeignKey(Workstation, name=_("Monday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= "Monday")
    tuesday = models.ForeignKey(Workstation, name=_("Tuesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name="Tuesday")
    wednesday = models.ForeignKey(Workstation, name=_("Wednesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Wednesday')
    thursday = models.ForeignKey(Workstation, name=_("Thursday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Thursday')
    friday = models.ForeignKey(Workstation, name=_("Friday"), blank = True, null = True,
            on_delete=models.SET_NULL, related_name = 'Friday')
    saturday = models.ForeignKey(Workstation, name=_("Saturday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Saturday')
    sunday = models.ForeignKey(Workstation, name=_("Sunday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'Sunday')

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.monday_date = calendar_functions.date_from_isoweek(self.year, self.week, 0)
        super(Userweek, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('employee', 'year', 'week')
