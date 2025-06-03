import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LeadsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("leads_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("leads_group", self.channel_name)

    async def receive(self, text_data):
        pass  # We are not expecting incoming messages

    async def lead_changed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'lead_changed',
            'message': event['message']
        }))

class dashboardLeadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'dashboard_leads_group'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group when disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Handle the lead_changed event and send updated lead counts
    async def lead_changed(self, event):
        # Send updated data (website_leads and ai_leads) to the WebSocket
        await self.send(text_data=json.dumps({
            'website_leads': event['website_leads'],
            'ai_leads': event['ai_leads'],
            'total_leads': event['total_leads'],
        }))


class sideBarLeadCountConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'sidebar_leads_group'

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group when disconnected
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def lead_changed(self, event):
        await self.send(text_data=json.dumps({
            'total_leads': event['total_leads'],
        }))
