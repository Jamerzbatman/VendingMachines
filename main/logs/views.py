from django.shortcuts import render

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone

from logs.models import Log

def view_short_term_logs(request):
    logs = Log.objects.short_term_logs(user=request.user)
    return render(request, 'logs/short_term_logs.html', {'logs': logs})

def view_long_term_logs(request):
    logs = Log.objects.long_term_logs(user=request.user)
    return render(request, 'logs/long_term_logs.html', {'logs': logs})


def add_log(job_id,medal, message, log_type, user, linked_log=None):
    new_Log = Log.objects.create(
        medal=medal,
        job_id=job_id,
        log_type=log_type,
        log_data=message,
        user=user,
        linked_log=linked_log
    )

    # Send the update to the WebSocket group
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'logs_{user.id}',  # Target the user's group
        {
            'type': 'log_update',
            'logs': message,
        }
    )   
    
    return new_Log


def Min_Short_Logs(request):
    user = request.user  # Ensure you have a user to filter by
    current_time = timezone.now()
    one_minute_ago = current_time - timedelta(minutes=1)
    
    # Get logs in the last minute
    recent_logs = Log.objects.filter(user=user, log_type='short', created_at__gte=one_minute_ago)

    # Prepare the logs for response
    logs_data = [
        {"message": log.log_data, "created_at": log.created_at.strftime('%Y-%m-%d %H:%M:%S')}
        for log in recent_logs
    ]
    
    # Return as JSON response
    return JsonResponse({"logs": logs_data})