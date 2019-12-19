from unittest import skip

from django.test import TestCase, Client
from django.urls import reverse

from accounts.models import Account, AccountManager

# TODO: add messages to asserts
class TestLoginUserView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.account_url = reverse('account')

        self.account = Account.objects.create(
            email='test@gmail.com', first_name='test', last_name='test',
        )
        self.account_password = 'ntcnNTCN1'
        self.account.set_password(self.account_password)
        self.account.save()

    def test_LoginUser_GET(self):
        response = self.client.get(self.login_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_LoginUser_POST_valid_credentials(self):
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )
        self.assertEquals(response, True)

        response = self.client.get(self.account_url)
        self.assertEqual(response.context['user'].email, self.account.email)

    def test_LoginUser_POST_no_login(self):
        response = self.client.login(username='', password=self.account_password)

        self.assertEquals(response, False)

    def test_LoginUser_POST_no_password(self):
        response = self.client.login(username=self.account.email, password='')

        self.assertEquals(response, False)

    def test_LoginUser_POST_no_password_no_login(self):
        response = self.client.login(username='', password='')

        self.assertEquals(response, False)

    def test_LoginUser_POST_invalid_credentials(self):
        response = self.client.login(username='invalid@gmail.com', password='invalid')

        self.assertEquals(response, False)


class TestRegistrationView(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
        self.registration_url = reverse('registration')

        self.reg_user = {
            'email': 'registration@gmail.com',
            'first_name': 'registration',
            'last_name': 'registration',
            'password': 'htubcnhfwbz',
        }

    def test_RegistrationView_GET(self):
        response = self.client.get(self.registration_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/registration.html')

    # TODO: add assertFormError
    # TODO: how to post password1 an password2
    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_valid_credentials(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': self.reg_user['email'],
                'first_name': self.reg_user['first_name'],
                'last_name': self.reg_user['last_name'],
                'password1': self.reg_user['password'],
                'password2': self.reg_user['password'],
            },
        )
        form_rendered = response.context['form']
        print("password1", form_rendered['password1'])
        print("password2", form_rendered['password2'])
        print("email", form_rendered['email'])
        all_accounts = Account.objects.all()
        for el in all_accounts:
            print(el)
        self.assertEquals(self.reg_user['email'], Account.objects.last().email)
        self.assertRedirects(response, self.home_url)

    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_password_mismatch(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': 'invalid',
                'first_name': 'invalid',
                'last_name': 'invalid',
                'password1': 'invalid1',
                'password2': 'invalid2',
            },
        )

        self.assertNotEquals(self.reg_user['email'], Account.objects.last().email)

    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_no_email(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': '',
                'first_name': self.reg_user['first_name'],
                'last_name': self.reg_user['last_name'],
                'password1': self.reg_user['password'],
                'password2': self.reg_user['password'],
            },
        )

        self.assertNotEquals(self.reg_user['email'], Account.objects.last().email)

    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_no_first_name(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': self.reg_user['email'],
                'first_name': '',
                'last_name': self.reg_user['last_name'],
                'password1': self.reg_user['password'],
                'password2': self.reg_user['password'],
            },
        )

        self.assertNotEquals(self.reg_user['email'], Account.objects.last().email)

    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_no_last_name(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': self.reg_user['email'],
                'first_name': self.reg_user['first_name'],
                'last_name': '',
                'password1': self.reg_user['password'],
                'password2': self.reg_user['password'],
            },
        )

        self.assertNotEquals(self.reg_user['email'], Account.objects.last().email)

    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_no_password1(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': self.reg_user['email'],
                'first_name': self.reg_user['first_name'],
                'last_name': self.reg_user['last_name'],
                'password1': '',
                'password2': self.reg_user['password'],
            },
        )

        self.assertNotEquals(self.reg_user['email'], Account.objects.last().email)

    @skip('Fields password1 and password2 cannot post')
    def test_RegistrationView_POST_no_password2(self):
        response = self.client.post(
            self.registration_url,
            {
                'email': self.reg_user['email'],
                'first_name': self.reg_user['first_name'],
                'last_name': self.reg_user['last_name'],
                'password1': self.reg_user['password'],
                'password2': '',
            },
        )

        self.assertNotEquals(self.reg_user['email'], Account.objects.last().email)


class TestAccountView(TestCase):
    def setUp(self):
        self.client = Client()
        self.account_url = reverse('account')

        self.account = Account.objects.create(
            email='test@gmail.com', first_name='test', last_name='test',
        )
        self.account_password = 'ntcnNTCN1'
        self.account.set_password(self.account_password)
        self.account.save()
        self.account_new_email = 'test1@gmail.com'
        self.required_field_error = 'This field is required.'

    def test_AccountView_GET_authorized_user(self):
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )
        self.assertEquals(response, True)

        response = self.client.get(self.account_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/account.html')

    def test_AccountView_GET_unauthorized_user(self):
        redirect_url = '/accounts/login/?next=/accounts/account/'
        response = self.client.get(self.account_url)
        self.assertRedirects(response, redirect_url)

    # TODO: should I restore changed values?
    def test_AccountView_POST_valid_credentials(self):
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )

        self.assertEquals(response, True)
        response = self.client.post(
            self.account_url,
            {
                'email': self.account_new_email,
                'first_name': self.account.first_name,
                'last_name': self.account.last_name,
            },
        )

        self.assertEquals(self.account_new_email, Account.objects.last().email)
        self.account.save()  # restore email

    def test_AccountView_POST_empty_first_name(self):
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )

        self.assertEquals(response, True)

        response = self.client.post(
            self.account_url,
            {
                'email': self.account.email,
                'first_name': '',
                'last_name': self.account.last_name,
            },
        )
        field = 'first_name'
        self.assertFormError(response, 'form', field, self.required_field_error)

    def test_AccountView_POST_empty_last_name(self):
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )

        self.assertEquals(response, True)

        response = self.client.post(
            self.account_url,
            {
                'email': self.account.email,
                'first_name': self.account.first_name,
                'last_name': '',
            },
        )
        field = 'last_name'
        self.assertFormError(response, 'form', field, self.required_field_error)

    def test_AccountView_POST_empty_email(self):
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )

        self.assertEquals(response, True)

        response = self.client.post(
            self.account_url,
            {
                'email': '',
                'first_name': self.account.first_name,
                'last_name': self.account.last_name,
            },
        )
        field = 'email'
        self.assertFormError(response, 'form', field, self.required_field_error)

    def test_AccountView_POST_existing_email(self):
        account = Account.objects.create(
            email='test2@gmail.com', first_name='test2', last_name='test2',
        )
        account_password = 'ntcnNTCN2'
        account.set_password(self.account_password)
        account.save()

        response = self.client.login(
            username=self.account.email, password=self.account_password
        )

        self.assertEquals(response, True)
        response = self.client.post(
            self.account_url,
            {
                'email': account.email,
                'first_name': self.account.first_name,
                'last_name': self.account.last_name,
            },
        )
        field = 'email'
        self.assertFormError(
            response, 'form', field, f'Email {account.email} is already exist.'
        )
        self.assertNotEquals(
            self.account.email, Account.objects.get(pk=account.id).email
        )


class TestLogoutUserView(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.account_url = reverse('account')

        self.account = Account.objects.create(
            email='test@gmail.com', first_name='test', last_name='test',
        )
        self.account_password = 'ntcnNTCN1'
        self.account.set_password(self.account_password)
        self.account.save()

    def test_LogoutUser_GET(self):
        response = self.client.get(self.logout_url)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/logout.html')

    def test_LogoutUser_GET_redirect_unauthorized_user(self):
        redirect_url = '/accounts/login/?next=/accounts/account/'
        response = self.client.login(
            username=self.account.email, password=self.account_password
        )

        self.assertEquals(response, True)

        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].email, self.account.email)

        response = self.client.logout()
        response = self.client.get(self.account_url)
        self.assertRedirects(response, redirect_url)
