import json

from channels.generic.websocket import AsyncWebsocketConsumer

from communications import init_container
from communications.entities.messages import Message
from communications.services.messages import SendMessageCommand


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        print(f"Connecting to room: {self.room_name}")  # Debug log

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"Accepted connection for room: {self.room_name}")  # Debug log

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']
        receiver_id = text_data_json['receiver_id']

        container = init_container()

        message_command = container.resolve(SendMessageCommand)
        message_command.handle(
            message=Message(sender_id=sender_id, receiver_id=receiver_id, content=message),
            room_name=self.room_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'receiver_id': receiver_id
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        receiver_id = event['receiver_id']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'receiver_id': receiver_id
        }))
