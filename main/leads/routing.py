from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/leads/$', consumers.LeadsConsumer.as_asgi()),
    re_path(r'ws/dashboardLeadConsumer/', consumers.dashboardLeadConsumer.as_asgi()),

]
