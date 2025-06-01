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
