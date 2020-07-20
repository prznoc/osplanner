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
    workstation = models.ForeignKey(Workstation, name=_('workstation'), on_delete=models.CASCADE)
    window = models.BooleanField(_('window'), default=False)
    noise = models.BooleanField(_('noise'), default=False)
    large_screen = models.BooleanField(_('large_screen'), default=False)
    is_mac = models.BooleanField(_('is_mac'), default=False)


class EmployeePreferences(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("employee"), on_delete=models.CASCADE)
    favourite_workspace = models.ManyToManyField(Workstation, name=_("favourite_workspace")) 
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
    monday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("monday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= "monday")
    tuesday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("tuesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name="tuesday")
    wednesday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("wednesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'wednesday')
    thursday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("thursday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'thursday')
    friday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("friday"), blank = True, null = True,
            on_delete=models.SET_NULL, related_name = 'friday')
    saturday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("saturday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'saturday')
    sunday = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("sunday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'sunday')

    def __str__(self):
        return str(str(self.workstation) + str(self.year)+ str(self.week))

    class Meta:
        unique_together = ('workstation', 'year', 'week')

class Userweek(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, name=_("employee"), on_delete=models.CASCADE)
    year =  models.IntegerField(_('year'))
    week = models.IntegerField(_('week'))
    monday_date = models.DateField(_("monday_date"))
    monday = models.ForeignKey(Workstation, name=_("monday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= "monday")
    tuesday = models.ForeignKey(Workstation, name=_("tuesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name="tuesday")
    wednesday = models.ForeignKey(Workstation, name=_("wednesday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'wednesday')
    thursday = models.ForeignKey(Workstation, name=_("thursday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'thursday')
    friday = models.ForeignKey(Workstation, name=_("friday"), blank = True, null = True,
            on_delete=models.SET_NULL, related_name = 'friday')
    saturday = models.ForeignKey(Workstation, name=_("saturday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'saturday')
    sunday = models.ForeignKey(Workstation, name=_("sunday"), blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = 'sunday')

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.monday_date = calendar_functions.date_from_isoweek(self.year, self.week, 1) #monday - 1
        super(Userweek, self).save(*args, **kwargs)
