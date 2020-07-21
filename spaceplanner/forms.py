from django import forms
from django.db.models import Q
from .models import EmployeePreferences, Userweek, Workstation, Workweek

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = EmployeePreferences
        fields = ('favourite_workspace', 'window', 'window_preference', 'noise', 'noise_preference', 'large_screen', 'large_screen_preference', 'is_mac', 'is_mac_preference')

#skomplikowane filtrowanie
class ScheduleForm(forms.ModelForm):
    '''
    monday_request = Workweek.objects.filter(Monday=None)
    Monday = forms.ModelChoiceField(queryset = Workstation.objects.filter(
        ws_id__in= [obj.workstation.ws_id for obj in monday_request])
    )
    '''
    Monday = forms.ModelChoiceField(queryset = Workstation.objects.filter(ws_id=1))
    class Meta:
        model = Userweek
        fields = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')

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
