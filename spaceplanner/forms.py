from django import forms
from django.db.models import Q
from .models import EmployeePreferences, Userweek, Workstation, Workweek

class UserPreferencesForm(forms.ModelForm):
    favourites = forms.ModelMultipleChoiceField(queryset=Workstation.objects.all(),
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = EmployeePreferences
        exclude = ('favourite_workspace', 'employee')

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = kwargs.setdefault('initial', {})
            initial['favourites'] = [t.pk for t in kwargs['instance'].favourite_workspace.all()]

        forms.ModelForm.__init__(self, *args, **kwargs)

    
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
    

#złożone filtrowanie
class ScheduleForm(forms.ModelForm):
    '''
    monday_request = Workweek.objects.filter(Monday=None, year=self.instance.year, week=self.instance.week)
    Monday = forms.ModelChoiceField(queryset = Workstation.objects.filter(
        ws_id__in= [obj.workstation.ws_id for obj in monday_request]), required=False
    )
    '''
    Monday = forms.ModelChoiceField(queryset = Workstation.objects.filter(ws_id=1), required=False)

    class Meta:
        model = Userweek
        fields = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

    '''
    def __init__

        self.instance
        self.initial
    '''

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
    weekdays = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,
                                          choices=OPTIONS)
