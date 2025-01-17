from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .utils import grid_pattern, callsign_pattern

class ExtendedUserCreationForm(UserCreationForm):
    station_callsign = forms.CharField(max_length=20)
    my_gridsquare = forms.CharField(max_length=6)

    def clean_station_callsign(self):
        callsign = self.cleaned_data['station_callsign'].upper()
        if not re.match(callsign_pattern, callsign):
            raise ValidationError("Invalid amateur radio callsign format")
        return callsign

    def clean_my_gridsquare(self):
        grid = self.cleaned_data['my_gridsquare'].upper()
        if not re.match(grid_pattern, grid):
            raise ValidationError("Invalid Maidenhead grid square format")
        return grid

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            from .models import UserDefaults
            UserDefaults.objects.create(
                user=user,
                station_callsign=self.cleaned_data['station_callsign'],
                my_gridsquare=self.cleaned_data['my_gridsquare']
            )
        return user

class UserDefaultsForm(forms.ModelForm):
    def clean_station_callsign(self):
        callsign = self.cleaned_data['station_callsign'].upper()
        if not re.match(callsign_pattern, callsign):
            raise ValidationError("Invalid amateur radio callsign format")
        return callsign

    def clean_my_gridsquare(self):
        grid = self.cleaned_data['my_gridsquare'].upper()
        if not re.match(grid_pattern, grid):
            raise ValidationError("Invalid Maidenhead grid square format")
        return grid

    class Meta:
        from .models import UserDefaults
        model = UserDefaults
        fields = ['station_callsign', 'my_gridsquare', 'mode', 'band', 'freq']
        labels = {
            'my_gridsquare': 'Grid Square',
            'station_callsign': 'Station Callsign',
            'freq': 'Default Frequency',
        } 