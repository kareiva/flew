from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from .utils import grid_pattern, callsign_pattern
from .models import UserDefaults


class ExtendedUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(username=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserDefaults.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = ("email", "password1")


class ProfileForm(forms.ModelForm):
    station_callsign = forms.CharField(max_length=20, required=False)
    my_gridsquare = forms.CharField(max_length=6, required=False)

    def clean_station_callsign(self):
        callsign = self.cleaned_data["station_callsign"]
        if callsign and not re.match(callsign_pattern, callsign.upper()):
            raise ValidationError("Invalid amateur radio callsign format")
        return callsign.upper() if callsign else callsign

    def clean_my_gridsquare(self):
        grid = self.cleaned_data["my_gridsquare"]
        if grid and not re.match(grid_pattern, grid.upper()):
            raise ValidationError("Invalid Maidenhead grid square format")
        return grid.upper() if grid else grid

    class Meta:
        model = UserDefaults
        fields = ["station_callsign", "my_gridsquare", "mode", "band", "freq"]
