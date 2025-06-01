from django.contrib import admin
from .models import Lead, LeadPhone, LeadEmail

admin.site.register(Lead)
admin.site.register(LeadPhone)
admin.site.register(LeadEmail)
