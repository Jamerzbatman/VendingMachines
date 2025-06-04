# main/celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from logs.views import add_log
from django.contrib.auth.models import User
import uuid

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    user = User.objects.first()
    job_id = str(uuid.uuid4())
    add_log(job_id, "Gold", f"Request: {self.request!r}", "long", user)
