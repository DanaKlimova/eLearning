import logging
from django.shortcuts import render, reverse
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


from accounts.forms import (
    AccountAuthenticationForm,
    RegistrationForm,
    AccountUpdateForm,
    OrganizationForm,
)
from accounts.models import Account, Organization


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


@method_decorator(login_required, name='dispatch')
class ManageOrganizationListView(ListView):
    model = Organization
    context_object_name = 'organization_list'
    template_name_suffix = "manage_list"

    def get_queryset(self):
        queryset = Organization.objects.filter(manager=self.request.user)
        return queryset


@method_decorator(login_required, name='dispatch')
class OrganizationListView(ListView):
    context_object_name = 'organization_list'

    def get_queryset(self):
        queryset = self.request.user.organizations.all()
        return queryset


@method_decorator(login_required, name='dispatch')
class CreateOrganizationView(FormView):
    template_name = "accounts/organization_edit.html"
    form_class = OrganizationForm
    model = Organization
    organization_pk = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['view'] = 'create'
        return kwargs

    def form_valid(self, form):
        form.instance.manager = self.request.user
        organization = form.save()
        success_url = reverse('organization_edit', kwargs={'organization_pk': organization.pk})
        return HttpResponseRedirect(success_url)

    def form_invalid(self, form):
        form.initial = {
            "name": self.request.POST.get("name"),
        }
        return self.render_to_response(self.get_context_data(form=form))


# TODO: transfer js code in static file
@method_decorator(login_required, name='dispatch')
class EditOrganizationView(FormView):
    template_name = "accounts/organization_edit.html"
    form_class = OrganizationForm
    model = Organization
    extra_context = {"success_message": ""}
    organization = None
    organization_pk = None

    def dispatch(self, request, *args, **kwargs):
        self.organization_pk = kwargs['organization_pk']
        try:
            self.organization = Organization.objects.get(pk=self.organization_pk)
        except Organization.DoesNotExist:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if self.organization.manager != request.user:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        return handler(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'instance': self.organization})
        return kwargs

    def get_initial(self):
        self.initial = {
            "name": self.organization.name,
        }
        return self.initial.copy()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.extra_context["success_message"] = "Organization updated"
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get(self, request, *args, **kwargs):
        self.extra_context["success_message"] = ""
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['organization_pk'] = self.organization_pk
        kwargs['view'] = 'edit'
        kwargs["employees"] = self.organization.employees.all()
        return kwargs

    def form_valid(self, form):
        form.initial = {
            "name": self.request.POST.get("name")
        }
        form.save()
        return render(self.request, self.template_name, self.get_context_data())


def add_employee(request, organization_pk):
    if request.method == "POST":
        try:
            organization = Organization.objects.get(pk=organization_pk)
        except Organization.DoesNotExist:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if organization.manager != request.user:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)

        employee_email = request.POST.get('email')
        try:
            employee = Account.objects.get(email=employee_email)
        except Account.DoesNotExist:
            redirect_url = reverse('organization_edit', kwargs={"organization_pk": organization_pk})
            return HttpResponseRedirect(redirect_url)

        organization.employees.add(employee)

        redirect_url = reverse('organization_edit', kwargs={"organization_pk": organization_pk})
        return HttpResponseRedirect(redirect_url)


@login_required
def sign_as(request, organization_pk):
    if request.method == "POST":
        try:
            organization = Organization.objects.get(pk=organization_pk)
        except Organization.DoesNotExist:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if organization.manager != request.user:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)

        request.user.organization = organization
        request.user.is_organization = True
        request.user.save()

        redirect_url = reverse('organization_list', kwargs={})
        return HttpResponseRedirect(redirect_url)


@login_required
def unsign_as(request, organization_pk):
    if request.method == "POST":
        try:
            organization = Organization.objects.get(pk=organization_pk)
        except Organization.DoesNotExist:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)
        if organization.manager != request.user:
            redirect_url = reverse('home', kwargs={})
            return HttpResponseRedirect(redirect_url)

        request.user.organization = None
        request.user.is_organization = False
        request.user.save()

        redirect_url = reverse('organization_list', kwargs={})
        return HttpResponseRedirect(redirect_url)