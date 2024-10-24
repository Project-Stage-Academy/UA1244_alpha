import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from communications import init_container
from communications.entities.messages import Message
from communications.services.messages import SendMessageCommand

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"
        logger.info(f"Attempting to connect to room: {self.room_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Connection accepted for room: {self.room_name}")

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting from room: {self.room_name} with code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        logger.debug(f"Received message data: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            sender_id = text_data_json['sender_id']
            receiver_id = text_data_json['receiver_id']

            logger.info(f"Message from sender: {sender_id} to receiver: {receiver_id} in room: {self.room_name}")

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
        except Exception as e:
            logger.error(f"Error processing received message: {e}", exc_info=True)

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        receiver_id = event['receiver_id']

        logger.debug(f"Broadcasting message: {message} from sender: {sender_id} to receiver: {receiver_id}")

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'receiver_id': receiver_id
        }))
