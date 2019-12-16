from django.test import SimpleTestCase
from django.urls import reverse, resolve

from accounts.views import (
    LoginUser,
    RegistrationView,
    AccountView,
    LogoutUser,
)


class TestUrls(SimpleTestCase):
    def test_login_url_resolves(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func.view_class, LoginUser)

    def test_registration_resolves(self):
        url = reverse('registration')
        self.assertEquals(resolve(url).func.view_class, RegistrationView)

    def test_account_resolves(self):
        url = reverse('account')
        self.assertEquals(resolve(url).func.view_class, AccountView)

    def test_logout_resolves(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func.view_class, LogoutUser)
