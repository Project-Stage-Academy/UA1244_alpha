import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

from communications.di_container import init_container
from communications.domain.entities.messages import Message
from communications.domain.exceptions.base import ApplicationException
from communications.domain.values.messages import Text
from communications.services.commands.messages import CreateMessageCommand
from communications.services.queries.messages import ChatRoomQuery


logger = logging.getLogger(__name__)

container = init_container()
create_message_command: CreateMessageCommand = container.resolve(CreateMessageCommand)
get_chat_room_query: ChatRoomQuery = container.resolve(ChatRoomQuery)

cipher_suite = Fernet(settings.ENCRYPTION_KEY)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_oid = self.scope['url_route']['kwargs']['room_oid']
        self.user_id = self.scope['user'].id
        self.room_group_name = f"chat_{self.room_oid}"
        logger.info(f"Attempting to connect to room: {self.room_oid}")

        chatroom = get_chat_room_query.handle(self.room_oid)
        if not chatroom or self.user_id not in [chatroom.sender_id, chatroom.receiver_id]:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"Connection accepted for room: {self.room_oid}")

    async def disconnect(self, close_code):
        logger.info(f"Disconnecting from room: {self.room_oid} with code: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        logger.debug(f"Received message data: {text_data}")
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']

            logger.info(f"Message in room: {self.room_oid}")

            message_entity = await create_message_command.handle(
                message_data=message,
                room_oid=self.room_oid,
                user_id=self.user_id
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'oid': message_entity.get("oid"),
                    'content': message_entity.get("content"),
                    'sender_id': message_entity.get("sender_id"),
                    'receiver_id': message_entity.get("receiver_id"),
                    'created_at': message_entity.get("created_at"),
                    'sender_name': message_entity.get('sender_name')
                }
            )
        except ApplicationException as e:
            logger.error(f"Error processing received message: {e}", exc_info=True)

    async def chat_message(self, event):
        oid = event['oid']

        try:
            content = cipher_suite.decrypt(event['content']).decode()
        except (InvalidToken, ValueError) as e:
            logger.error(f"Decryption failed for message oid {oid}: {e}", exc_info=True)
            await self.send(text_data=json.dumps({
                'error': 'Failed to decrypt message. Invalid or corrupted data.',
                'oid': oid
            }))
            return

        sender_id = event['sender_id']
        receiver_id = event['receiver_id']
        created_at = event['created_at'].isoformat()
        sender_name = event['sender_name']

        await self.send(text_data=json.dumps({
            'oid': oid,
            'content': content,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'created_at': created_at,
            'sender_name': sender_name
        }))
