from django import forms
from .models import EmployeePreferences

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = EmployeePreferences
        fields = ('favourite_workspace', 'window', 'window_preference', 'noise', 'noise_preference', 'large_screen', 'large_screen_preference', 'is_mac', 'is_mac_preference')