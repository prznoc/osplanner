from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator 

from datetime import datetime, timedelta

class Workstation(models.Model):
    ws_id = models.IntegerField(primary_key=True, unique = True)
    window = models.BooleanField(default = False)
    noise = models.BooleanField(default = False)
    large_screen = models.BooleanField(default = False)
    is_mac = models.BooleanField(default = False)

    def __str__(self):
        return str(self.ws_id)

    #@transaction.commit_on_success
    def save(self, *args, **kwargs):
        if self._state.adding is True:
            today = datetime.today()
            next_monday = today + timedelta(days=-today.weekday(), weeks=1)
            while (next_monday.year == today.year):
                week = Workweek(workstation = self, start_date = next_monday)
                week.save()
                next_monday = next_monday + timedelta(days = 7)
        super(Workstation, self).save(*args, **kwargs)

class User(models.Model):
    us_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    favourite_workspace = models.ForeignKey(Workstation, blank = True, null = True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return str(self.name)

    #def save(self, *args, **kwargs):
    
class Preferences(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    window = models.BooleanField(default = False)
    window_preference = models.IntegerField(default = 1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    noise = models.BooleanField(default = False)
    noise_preference = models.IntegerField(default = 1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    large_screen = models.BooleanField(default = False)
    large_screen_preference = models.IntegerField(default = 1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    is_mac = models.BooleanField(default = False)
    is_mac_preference = models.IntegerField(default = 1, validators=[MinValueValidator(1), MaxValueValidator(3)])

class Workweek(models.Model):
    week_id = models.AutoField(primary_key=True)
    workstation = models.ForeignKey(Workstation, on_delete=models.CASCADE)
    start_date = models.DateField() #date of week's monday
    monday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name='monday')
    tuesday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'tuesday')
    wednesday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'wednesday')
    thursday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'thursday')
    friday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'friday')
    saturday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'saturday')
    sunday = models.ForeignKey(User, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'sunday')

    def __str__(self):
        return str(str(self.workstation) + str(self.start_date) + str(self.week_id))

    class Meta:
        unique_together = ('workstation', 'start_date')

