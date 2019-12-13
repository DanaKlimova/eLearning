from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView, UpdateView
from django.http import HttpResponse

from accounts.forms import (
    AccountAuthenticationForm,
    RegistrationForm,
    AccountUpdateForm,
)
from accounts.models import Account


class LoginUser(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = AccountAuthenticationForm


class RegistrationView(FormView):
    template_name = "accounts/registration.html"
    form_class = RegistrationForm
    success_url = 'home'

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password1")
        account = authenticate(email=email, password=password)
        login(self.request, account)
        return HttpResponseRedirect(reverse(self.get_success_url()))


class AccountView(FormView):
    template_name = "accounts/account.html"
    form_class = AccountUpdateForm
    model = Account
    success_url = 'account'
    extra_context = {"success_message": ""}

    def form_valid(self, form):
        form.initial = {
                "email": self.request.POST.get("email"),
                "first_name": self.request.POST.get("first_name"),
                "last_name": self.request.POST.get("last_name"),
            }
        form.save()
        return render(self.request, self.template_name, self.get_context_data()) 

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.request.user})
        return kwargs

    def get_initial(self):
        self.initial = {
            "email": self.request.user.email,
            "first_name": self.request.user.first_name,
            "last_name": self.request.user.last_name,
        }
        return self.initial.copy()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.extra_context["success_message"] = "Account updated"
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())


def logout_view(request):
    logout(request)
    return redirect("home")
