import calendar

from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from datetime import datetime

from .models import EmployeePreferences, Userweek, Workstation, Workweek

class UserPreferencesForm(forms.ModelForm):

    preferences_set = [_("is_mac"), _("window"), _("noise"), _("large_screen")]

    favourites = forms.ModelMultipleChoiceField(queryset=Workstation.objects.all(),
        widget=forms.CheckboxSelectMultiple, required=False, label=_("Choose favourite workstations:"))

    class Meta:
        model = EmployeePreferences
        exclude = ('favourite_workspace', 'employee')

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['favourites'] = [t.pk for t in kwargs['instance'].favourite_workspace.all()]
        forms.ModelForm.__init__(self, *args, **kwargs)
        for preference in self.preferences_set:
            self.fields[preference+'_preference'].label = mark_safe((preference.capitalize() + " priority" ':' + '<br />').replace("_", " "))

    def save(self, commit=True):        #Save overwrite neccessary because many-to-many relations needs them to work with forms
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

    this_week_flag = None

    class Meta:
        model = Userweek
        exclude = ('employee', 'year', 'week', 'monday_date')
    
    def __init__(self, *args, **kwargs):
        self.this_week_flag = kwargs.pop('flag')
        super(ScheduleForm, self).__init__(*args, **kwargs)
        workweeks = Workweek.objects.filter(year=self.instance.year, week=self.instance.week)
        for weekday in list(calendar.day_name):
            request = []
            for workweek in workweeks:
                attr = getattr(workweek, weekday)
                if not attr or attr == self.instance.employee:
                    request.append(workweek.workstation)
            request = Workstation.objects.filter(ws_id__in=[rq.ws_id for rq in request])
            self.fields[weekday] = forms.ModelChoiceField(queryset= request, required= False, label= mark_safe(weekday + ':' + '<br />'))
            self.initial[weekday] = getattr(self.instance, weekday)
            if self.this_week_flag and list(calendar.day_name).index(weekday) < datetime.today().weekday():
                self.fields[weekday].widget = forms.HiddenInput()
                self.fields[weekday].label = ''


class WeekdaysForm(forms.Form):

    weekdays = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, label=_("Choose days to schedule"))

    def __init__(self, *args, **kwargs):
        instance = kwargs.pop('instance')
        this_week_flag = kwargs.pop('flag')
        super(WeekdaysForm, self).__init__(*args, **kwargs)
        OPTIONS = []
        for weekday in list(calendar.day_name):
            if this_week_flag and list(calendar.day_name).index(weekday) < datetime.today().weekday():
                pass
            else:
                OPTIONS.append((weekday, weekday))
        self.fields['weekdays'].choices = tuple(OPTIONS)
        self.fields['weekdays'].initial = [weekday for weekday in list(calendar.day_name) if getattr(instance, weekday)]
        self.fields['weekdays'].required = False

            
class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
