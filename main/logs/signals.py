# logs/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Log

@receiver(post_save, sender='GoogleAPIJob')
def create_log_on_job_save(sender, instance, created, **kwargs):
    if created:
        # Create a long-term log
        long_log = Log.objects.create(
            job_id=instance.job_id,
            log_type='long',
            log_data='Google API Job started...',
            user=instance.user
        )

        # Create a short-term log
        Log.objects.create(
            job_id=instance.job_id,
            log_type='short',
            log_data='Started Google API, found 10 addresses',
            user=instance.user,
            linked_log=long_log  # Linking to the long-term log
        )
