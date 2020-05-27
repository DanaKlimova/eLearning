import logging
from django.shortcuts import render, reverse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


from accounts.forms import (
    AccountAuthenticationForm,
    RegistrationForm,
    AccountUpdateForm,
)
from accounts.models import Account


logger = logging.getLogger('eLearning')


class LoginUser(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = AccountAuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        logger.info(f'Security check complete. Loged {user} in.')
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        logger.info("User entered invalid credentials. User didn't log in.")
        return self.render_to_response(self.get_context_data(form=form))


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
        logger.info(f'{email} registered. Loged {email} in.')
        return HttpResponseRedirect(reverse(self.get_success_url()))

    def form_invalid(self, form):
        logger.info("User entered invalid credentions. User didn't register.")
        form.initial = {
            "email": self.request.POST.get("email"),
            "first_name": self.request.POST.get("first_name"),
            "last_name": self.request.POST.get("last_name"),
        }
        return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required, name='dispatch')
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
            logger.info(f'{request.user} updated account data.')
            return self.form_valid(form)
        else:
            logger.info(f"{request.user} didn't update account data.")
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())


class LogoutUser(LogoutView):
    template_name = 'main/home.html'

    @never_cache
    def dispatch(self, request, *args, **kwargs):
        logger.info(f'Loged {request.user} out.')
        logout(request)
        next_page = self.get_next_page()
        if next_page:
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)
