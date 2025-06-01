from django.db import models
from django.contrib.auth.models import User

class LeadSearchSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='lead_settings')
    numbLeads = models.IntegerField(default=10)
    keywords = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Search Settings for {self.user.username}"

class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=255)  # Optional name like "Google Maps", "Yelp", etc.
    key = models.CharField(max_length=512)   # API keys are long strings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} key for {self.user.username}"
    
class LocationPoints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='location_points')
    location_name = models.CharField(max_length=255)
    points = models.JSONField()  # Stores a list of lat/lng dicts

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location_name} - {len(self.points)} Points"
