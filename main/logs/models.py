from django.db import models
from django.contrib.auth.models import User

class LogManager(models.Manager):
    def short_term_logs(self, user):
        return self.filter(user=user, log_type='short').order_by('-created_at')

    def long_term_logs(self, user):
        return self.filter(user=user, log_type='long').order_by('-created_at')

# Add the custom manager to your Log model
class Log(models.Model):
    medal = models.CharField(max_length=100, null=True, blank=True)
    job_id = models.CharField(max_length=255)
    log_type = models.CharField(max_length=50, choices=[('short', 'Short Term'), ('long', 'Long Term')])
    log_data = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    linked_log = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Log {self.job_id} for {self.user.username}"