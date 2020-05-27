from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Account, Organization


class AccountAuthenticationForm(forms.ModelForm):
    user = None

    class Meta:
        model = Account
        fields = ("email", "password")
        widgets = {
            'password': forms.PasswordInput,
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data.get("email")
            password = self.cleaned_data.get("password")
            self.user = authenticate(email=email, password=password)
            if not self.user:
                raise forms.ValidationError("Invalid email or password")

    def get_user(self):
        if self.is_valid():
            return self.user


class RegistrationForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ("email", "first_name", "last_name", "password1", "password2")


class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("email", "first_name", "last_name")

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data.get("email")
            try:
                account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
            except Account.DoesNotExist:
                return email
            raise forms.ValidationError(f"Email {email} is already exist.")


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = (
            'name',
        )
