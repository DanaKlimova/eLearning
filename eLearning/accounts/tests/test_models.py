from django.test import TestCase
from django.urls import reverse

from accounts.models import AccountManager, Account

# TODO: add messages to asserts
class TestModels(TestCase):
    def test_create_user(self):
        Account.objects.create_user(
            email='test@gmail.com', first_name='test', last_name='test', password='test'
        )
        self.assertEquals(Account.objects.last().email, 'test@gmail.com')

    def test_create_superuser(self):
        Account.objects.create_superuser(
            email='test@gmail.com', first_name='test', last_name='test', password='test'
        )
        self.assertEquals(Account.objects.last().email, 'test@gmail.com')
        self.assertTrue(Account.objects.last().is_superuser)

    def test_account_no_email(self):
        try:
            Account.objects.create_user(
                email='', first_name='test', last_name='test', password='test'
            )
        except ValueError as ex:
            self.assertTrue('User must have an email address.' in str(ex))
        except:
            self.fail('Unexpected exception raised')
        else:
            self.fail('Expected exception not raised')

    def test_account_no_first_name(self):
        try:
            Account.objects.create_user(
                email='test', first_name='', last_name='test', password='test'
            )
        except ValueError as ex:
            self.assertTrue('User must have a first name.' in str(ex))
        except:
            self.fail('Unexpected exception raised')
        else:
            self.fail('Expected exception not raised')

    def test_account_no_last_name(self):
        try:
            Account.objects.create_user(
                email='test', first_name='test', last_name='', password='test'
            )
        except ValueError as ex:
            self.assertTrue('User must have a last name.' in str(ex))
        except:
            self.fail('Unexpected exception raised')
        else:
            self.fail('Expected exception not raised')

    def test_account_no_password(self):
        try:
            Account.objects.create_user(
                email='test', first_name='test', last_name='test', password=''
            )
        except ValueError as ex:
            self.assertTrue('User must have a password.' in str(ex))
        except:
            self.fail('Unexpected exception raised')
        else:
            self.fail('Expected exception not raised')
