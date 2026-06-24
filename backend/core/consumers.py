from channels.generic.websocket import AsyncWebsocketConsumer
import json

class DashboardConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "dashboard"

        await self.channel_layer.group_add(
            self.group_name,  # e.g., "dashboard"
            self.channel_name # unique channel for this connection
        )

        await self.accept()

        await self.send(text_data=json.dumps({
            "message": "Websocket Connected"
        }))

    async def disconnect(self, close_node):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        
        print("WebSocket disconneted")

    async def receive(self, text_data):
        data = json.loads(text_data)

        await self.send(text_data = json.dumps({
            "echo": data
        }))

    async def dashboard_message(self, event):   
        await self.send(text_data = json.dumps({
            "type": "dashboard_update",
            "data": event["data"]
        }))

    async def send_alert(self, event):
        await self.send(text_data = json.dumps({
            "type": "alert",
            "data": event["data"]   
        }))

