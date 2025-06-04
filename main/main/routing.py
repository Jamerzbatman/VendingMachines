from django.urls import re_path
from leads import consumers as leads
from logs import consumers as logs

websocket_urlpatterns = [
    re_path(r'ws/leads/$', leads.LeadsConsumer.as_asgi()),
    re_path(r'ws/dashboardLeadConsumer/', leads.dashboardLeadConsumer.as_asgi()),
    re_path(r'ws/sideBarLeadCount/', leads.sideBarLeadCountConsumer.as_asgi()),

    re_path(r'ws/logs/$', logs.LogConsumer.as_asgi()),  # WebSocket route for logs

]
