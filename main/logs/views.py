from django.shortcuts import render
from .models import Log

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
    return new_Log