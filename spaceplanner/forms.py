import calendar

from django import forms
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils.safestring import mark_safe
from datetime import datetime, timedelta

from .models import EmployeePreferences, Userweek, Workstation, Workweek

class UserPreferencesForm(forms.ModelForm):

    preferences_set = ["is_mac", "window", "noise", "large_screen"]

    favourites = forms.ModelMultipleChoiceField(queryset=Workstation.objects.all(),
        widget=forms.CheckboxSelectMultiple, required=False, label="Choose favourite workstations")

    class Meta:
        model = EmployeePreferences
        exclude = ('favourite_workspace', 'employee')

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['favourites'] = [t.pk for t in kwargs['instance'].favourite_workspace.all()]
        forms.ModelForm.__init__(self, *args, **kwargs)
        for preference in self.preferences_set:
            self.fields[preference+'_preference'].label = mark_safe(preference.capitalize() + " priority" ':' + '<br />')


    
    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m
        def save_m2m():
           old_save_m2m()
           instance.favourite_workspace.clear()
           for favourite in self.cleaned_data['favourites']:
                instance.favourite_workspace.add(favourite)
        self.save_m2m = save_m2m

        instance.save()
        self.save_m2m()

        return instance
    

class ScheduleForm(forms.ModelForm):

    class Meta:
        model = Userweek
        exclude = ('employee', 'year', 'week', 'monday_date')
    
    def __init__(self, *args, **kwargs):
        this_week_flag = kwargs.pop('flag')
        super(ScheduleForm, self).__init__(*args, **kwargs)
        for weekday in list(calendar.day_name):
            workweeks = Workweek.objects.filter(year=self.instance.year, week=self.instance.week)
            request = []
            for workweek in workweeks:
                attr = getattr(workweek, weekday)
                if not attr or attr == self.instance.employee:
                    request.append(workweek.workstation)
            request = Workstation.objects.filter(ws_id__in=[rq.ws_id for rq in request])
            self.fields[weekday] = forms.ModelChoiceField(queryset= request, required=False, label=mark_safe(weekday + ':' + '<br />'))
            self.initial[weekday] = getattr(self.instance, weekday)
            if this_week_flag and list(calendar.day_name).index(weekday) < datetime.today().weekday():
                self.fields[weekday].disabled = True


class WeekdayWidget(forms.CheckboxSelectMultiple):

    def create_option(self, *args, **kwargs):
        options_dict = super().create_option(*args, **kwargs)

        if self.attrs['this_week_flag'] == "True" and list(calendar.day_name).index(options_dict['value']) < datetime.today().weekday():
            #pass
            options_dict['attrs']['disabled'] = ''

        return options_dict


    
class WeekdaysForm(forms.Form):
    OPTIONS = (
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    )
    weekdays = forms.MultipleChoiceField(widget=WeekdayWidget,
                                          choices=OPTIONS, label="Choose days to schedule")

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')
        this_week_flag = kwargs.pop('flag')
        super(WeekdaysForm, self).__init__(*args, **kwargs)
        self.fields['weekdays'].widget = WeekdayWidget()
        if this_week_flag: self.fields['weekdays'].widget.attrs['this_week_flag'] = 'True'
        else: self.fields['weekdays'].widget.attrs['this_week_flag'] = 'False'
        self.fields['weekdays'].choices = self.OPTIONS
        self.fields['weekdays'].initial = [weekday for weekday in list(calendar.day_name) if getattr(instance, weekday)]
        self.fields['weekdays'].required = False

            
class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    '''
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field] = forms.Field(required=False, label=mark_safe(field + ':' + '<br />'))
    '''