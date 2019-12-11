from django import forms
from django.contrib.auth import authenticate

from accounts.models import Account


class AccountAuthenticationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("email", "password")
        widgets = {
            'password': forms.PasswordInput,
        }

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data.get("email")
            password = self.cleaned_data.get("password")
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid email or password")