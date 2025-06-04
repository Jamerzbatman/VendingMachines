# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from logs.models import Log
from django.utils import timezone
from datetime import timedelta

@receiver(post_save, sender=Log)
def send_log_update_on_save(sender, instance, created, **kwargs):
    """ Trigger WebSocket update when a log is saved (added or updated) """
    send_log_update(instance.user)

@receiver(post_delete, sender=Log)
def send_log_update_on_delete(sender, instance, **kwargs):
    """ Trigger WebSocket update when a log is deleted """
    send_log_update(instance.user)

def send_log_update(user):
    """ Send updated logs to the WebSocket group for the user """
    channel_layer = get_channel_layer()

    current_time = timezone.now()

    # Get logs created within the last 1 minute
    logs = Log.objects.filter(user=user, created_at__gte=current_time - timedelta(minutes=1)).order_by('-created_at')[:10]

    # Logs older than 1 minute shouldn't be sent in updates
    logs_data = [{"created_at": log.created_at.strftime('%Y-%m-%d %H:%M:%S'), "message": log.log_data} for log in logs]

    # Send the updated logs to the user's WebSocket group
    async_to_sync(channel_layer.group_send)(
        f'logs_{user.id}',  # Target the user's group
        {
            'type': 'log_update',  # This type will trigger the log_update method in your consumer
            'logs': logs_data
        }
    )
