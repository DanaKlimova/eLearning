from __future__ import absolute_import, unicode_literals
from datetime import datetime, timedelta

from eLearning.celery import app
from accounts.models import Account
from django.core.mail import send_mail
from django.conf import settings


@app.task
def send_email_starter():
    account_ids = list(
        Account.objects.filter(
            last_login__lt=datetime.now() - timedelta(settings.NATIFICATION_DATE),
        ).values_list("id", flat=True)
    )
    for account_id in account_ids:
        send_email.delay(account_id)


@app.task
def send_email(account_id):
    user = Account.objects.get(id=account_id)
    data = f"Dear {user.first_name}, you have not been visiting courses for a week!" \
           f"\nBest, eLearning team"
    send_mail('eLearning!', data, "eLearning",
              user.email, fail_silently=False)

