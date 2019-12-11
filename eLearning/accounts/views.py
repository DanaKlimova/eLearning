from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from accounts.forms import (
    AccountAuthenticationForm,
    RegistrationForm,
    AccountUpdateForm,
)
from accounts.models import Account


def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AccountAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect("home")
    else:
        form = AccountAuthenticationForm()

    context["login_form"] = form
    return render(request, "accounts/login.html", context=context)


def registration_view(request):
    context = {}

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password1")
            account = authenticate(email=email, password=password)
            login(request, account)
            return redirect("home")
        else:
            context["registration_form"] = form
    else:
        form = RegistrationForm()
        context["registration_form"] = form
    return render(request, "accounts/registration.html", context=context)


def account_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    context = {}

    if request.method == "POST":
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST.get("email"),
                "first_name": request.POST.get("first_name"),
                "last_name": request.POST.get("last_name"),
            }
            form.save()
            context["success_message"] = "Account updated"
    else:
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
            }
        )
    context["account_form"] = form
    return render(request, "accounts/account.html", context=context)


def logout_view(request):
    logout(request)
    return redirect("home")
