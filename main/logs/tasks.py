from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from logs.models import Log

@shared_task
def update_recent_logs():
    """ Periodic task to send logs created in the last minute to the WebSocket """
    current_time = timezone.now()

    # Get the logs created in the last minute
    recent_logs = Log.objects.filter(created_at__gte=current_time - timedelta(minutes=1)) \
                             .order_by('-created_at') \
                             .values('id', 'user_id', 'created_at', 'log_data') \
                             .all()

    # Get the channel layer for WebSocket communication
    channel_layer = get_channel_layer()

    for log in recent_logs:
        # Send the recent log to the WebSocket group
        async_to_sync(channel_layer.group_send)(
            f'logs_{log["user_id"]}',  # Target user's WebSocket group
            {
                'type': 'log_update',  # Custom event type
                'logs': [{  # Ensure it's a list with 'logs' key
                    'id': log['id'],
                    'created_at': log['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    'message': log['log_data']
                }]
            }
        )
