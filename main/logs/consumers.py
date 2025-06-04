# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_group_name = f'logs_{self.user.id}'  # User-specific group

        # Join the group (room) for the user
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when the WebSocket disconnects
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Handle log updates (new logs being added)
    async def log_update(self, event):
        logs = event['logs']  # Accessing the logs list, as the backend sends this

        # Send the log update to the frontend
        await self.send(text_data=json.dumps({
            'logs': logs  # Send the 'logs' as is to the frontend
        }))
