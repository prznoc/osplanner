from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy  as _
from django.conf import settings

from .app_logic import calendar_functions

class Workstation(models.Model):
    ws_id = models.AutoField(primary_key=True)
    label = models.CharField(verbose_name=_('label'), unique=True, max_length=100)

    def __str__(self):
        return str(self.label)


class WorkstationPreferences(models.Model):
    workstation = models.OneToOneField(Workstation, verbose_name=_('workstation'), on_delete=models.CASCADE)
    window = models.BooleanField(verbose_name=_('Window'), default=False)
    noise = models.BooleanField(verbose_name=_('Noise'), default=False)
    large_screen = models.BooleanField(verbose_name=_('Large_screen'), default=False)
    is_mac = models.BooleanField(verbose_name=_('Mac'), default=False)


class EmployeePreferences(models.Model):
    employee = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("employee"), on_delete=models.CASCADE)
    favourite_workspace = models.ManyToManyField(Workstation, verbose_name=_("favourite_workspace"), default = None, blank=True) 
    window = models.BooleanField(verbose_name=_('Window'), default = False)
    window_preference = models.IntegerField(verbose_name=_('Window priority'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])
    noise = models.BooleanField(verbose_name=_('Noise'), default = False)
    noise_preference = models.IntegerField(verbose_name=_('Noise priority'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])
    large_screen = models.BooleanField(verbose_name=_('Large screen'), default = False)
    large_screen_preference = models.IntegerField(verbose_name=_('Large screen priority'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])
    is_mac = models.BooleanField(verbose_name=_('Mac'), default = False)
    is_mac_preference = models.IntegerField(verbose_name=_('Mac priority'), default = 0, validators=[MinValueValidator(0), 
            MaxValueValidator(3)])


class Workweek(models.Model):
    week_id = models.AutoField(primary_key=True)
    workstation = models.ForeignKey(Workstation, name="workstation", on_delete=models.CASCADE, verbose_name=_('workstation'))
    year =  models.IntegerField(verbose_name=_('year'))
    week = models.IntegerField(verbose_name=_('week'))
    Monday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Monday", blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= _("Monday"))
    Tuesday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Tuesday", blank = True, null = True, 
            on_delete=models.SET_NULL, related_name=_("Tuesday"),)
    Wednesday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Wednesday", blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _("Wednesday"),)
    Thursday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Thursday", blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _("Thursday"),)
    Friday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Friday", blank = True, null = True,
            on_delete=models.SET_NULL, related_name = _("Friday"),)
    Saturday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Saturday", blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _("Saturday"),)
    Sunday = models.ForeignKey(settings.AUTH_USER_MODEL, name="Sunday", blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _("Sunday"),)

    def __str__(self):
        return str(str(self.workstation) + str(self.year)+ str(self.week))

    class Meta:
        unique_together = ('workstation', 'year', 'week')

class Userweek(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('employee'))
    year =  models.IntegerField(_('year'))
    week = models.IntegerField(_('week'))
    monday_date = models.DateField(_("monday_date"))
    Monday = models.ForeignKey(Workstation, blank = True, null = True, 
            on_delete=models.SET_NULL, related_name= _("Monday"))
    Tuesday = models.ForeignKey(Workstation, blank = True, null = True, 
            on_delete=models.SET_NULL, related_name=_("Tuesday"))
    Wednesday = models.ForeignKey(Workstation, blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _('Wednesday'))
    Thursday = models.ForeignKey(Workstation, blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _('Thursday'))
    Friday = models.ForeignKey(Workstation, blank = True, null = True,
            on_delete=models.SET_NULL, related_name = _('Friday'))
    Saturday = models.ForeignKey(Workstation, blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _('Saturday'))
    Sunday = models.ForeignKey(Workstation, blank = True, null = True, 
            on_delete=models.SET_NULL, related_name = _('Sunday'))

    def __str__(self):
        return str(str(self.employee) + str(self.year)+ str(self.week))

    def save(self, *args, **kwargs):
        if self._state.adding is True:
            self.monday_date = calendar_functions.date_from_isoweek(self.year, self.week, 0)
        super(Userweek, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('employee', 'year', 'week')
