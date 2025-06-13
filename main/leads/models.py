from django.db import models

class Lead(models.Model):
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('ai', 'AI'),
        ('google', 'Google'),
        ('brochures', 'Brochures'),
    ]

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    logo = models.URLField(max_length=500, blank=True)
    company_name = models.CharField(max_length=255, blank=True)
    address = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    company_website = models.CharField(max_length=255, blank=True)  # fix max_length
    num_machines = models.IntegerField(blank=True, null=True)
    types = models.TextField(blank=True, null=True)
    setup_time = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    ai_recommendation = models.TextField(blank=True, null=True)
    ai_reasons = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.company_name}'

class LeadPhone(models.Model):
    lead = models.ForeignKey(Lead, related_name='phones', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return self.phone_number

class LeadEmail(models.Model):
    lead = models.ForeignKey(Lead, related_name='emails', on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.email
