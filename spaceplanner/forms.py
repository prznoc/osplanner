from django import forms
from .models import EmployeePreferences, Userweek

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = EmployeePreferences
        fields = ('favourite_workspace', 'window', 'window_preference', 'noise', 'noise_preference', 'large_screen', 'large_screen_preference', 'is_mac', 'is_mac_preference')

class ScheduleForm(forms.ModelForm):
    
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
