# main/celery.py

from __future__ import absolute_import, unicode_literals
import os
import uuid
from celery import Celery
# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

from django.contrib.auth import get_user_model

import django
django.setup()
from logs.views import add_log



app = Celery('main')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    # Use a sample user to record debug information
    User = get_user_model()
    user = User.objects.first()
    if user:
        add_log(str(uuid.uuid4()), "Gold", f"Request: {self.request!r}", "long", user)
