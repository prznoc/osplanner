from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 


class Workstand(models.Model):
    ws_id = models.IntegerField(primary_key=True, unique = True)

    def __str__(self):
        return str(self.ws_id)


class Properties(models.Model):
    workstand = models.OneToOneField(Workstand, on_delete=models.CASCADE, primary_key = True)
    window = models.IntegerField(default = 1, validators=[MaxValueValidator(3), MinValueValidator(1)])
    noise = models.IntegerField(default = 1, validators=[MaxValueValidator(5), MinValueValidator(1)])
    large_screen = models.BooleanField(default = False)
    is_mac = models.BooleanField(default = False)
    

class User(models.Model):
    us_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return str(self.name)

class Preference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True)
    window = models.IntegerField(default = 1, validators=[MinValueValidator(1), MaxValueValidator(3)])
    noise = models.IntegerField(default = 1, validators=[MaxValueValidator(1), MinValueValidator(5)])
    large_screen = models.BooleanField(default = False)
    is_mac = models.BooleanField(default = False)

class Workweek(models.Model):
    workstand = models.ForeignKey(Workstand, on_delete=models.CASCADE)
    start_date = models.DateField(primary_key = True)
    monday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name='monday')
    tuesday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'tuesday')
    wednesday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'wednesday')
    thursday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'thursday')
    friday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'friday')
    saturday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'saturday')
    sunday = models.ForeignKey(User, default= None, blank = True, null = True, on_delete=models.SET_NULL,
    related_name = 'sunday')

