import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eLearning.settings")

app = Celery("eLearning")  # pylint: disable=invalid-name
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
