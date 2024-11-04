import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from communications.di_container import init_container
from communications.domain.entities.messages import Message
from communications.domain.exceptions.base import ApplicationException
from communications.domain.values.messages import Text
from communications.services.commands.messages import CreateMessageCommand
from communications.services.queries.messages import ChatRoomQuery


logger = logging.getLogger(__name__)

container = init_container()
create_message_command = container.resolve(CreateMessageCommand)
get_chat_room_query = container.resolve(ChatRoomQuery)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_oid = self.scope['url_route']['kwargs']['room_oid']
        self.user_id = self.scope['user'].id
        self.room_group_name = f"chat_{self.room_oid}"
        logger.info(f"Attempting to connect to room: {self.room_oid}")

        chatroom = await get_chat_room_query.handle(self.room_oid)
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

            await create_message_command.handle(
                message=Message(content=Text(value=message)),
                room_oid=self.room_oid
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                }
            )
        except ApplicationException as e:
            logger.error(f"Error processing received message: {e}", exc_info=True)

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message,
        }))
