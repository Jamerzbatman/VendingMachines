from django.contrib import admin
from .models import LeadSearchSetting, ApiKey, LocationPoints

admin.site.register(LeadSearchSetting)
admin.site.register(ApiKey)
admin.site.register(LocationPoints)
